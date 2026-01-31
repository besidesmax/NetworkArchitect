from typing import List, Dict, Any

from PySide6.QtCore import QObject, Signal, Property, Slot, QTimer

from models.database_service import DatabaseService
from models.game_session import GameSession
from models.bridge_type import BridgeType


class GameViewModel(QObject):
    """MVVM ViewModel coordinating game state for Network Architect."""

    # Signals for view notifications
    nodes_changed = Signal()
    budget_changed = Signal(int)
    time_updated = Signal(str)
    confirm_navigation = Signal(str)
    game_reset = Signal()
    level_completed = Signal(int, int, str)  # redundancy_score, performance_score, time (mm:ss)
    error_occurred = Signal(str)
    bridge_type_changed = Signal()
    bridge_placed = Signal()
    bridge_removed = Signal()

    def __init__(self, player_id: int, level_id: int, db_service: DatabaseService):
        """
        Initialize ViewModel with DatabaseService dependency injection.

        Args:
            player_id: ID of the selected player
            level_id: ID of the selected level
            db_service: Persistence layer for loading levels/game sessions.
        """
        super().__init__()
        self._db_service: DatabaseService = db_service

        # start GameSession
        self._player = self._db_service.get_player_by_id(player_id)
        self._level = self._db_service.get_level(level_id)
        self._game_session = GameSession(self._player, self._level)

        # provide GameBoard
        grid_points = self._level.game_board
        self._game_board: List = []
        for g in grid_points:
            self._game_board.append({"id": g.grid_point_id, "x": g.position_x, "y": g.position_y})

        # Timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer_tick)
        self._elapsed_seconds = 0
        self.resume_timer()

        # bridge placement
        self._selected_bridge_type: BridgeType | None = None

    # === PROPERTIES ===
    @Property(list)
    def game_board(self) -> List[Dict[str, Any]]:
        """all GridPoints of the GameBoard"""
        return self._game_board

    @Property(list, notify=nodes_changed)
    def nodes(self) -> List[Dict[str, Any]]:
        """All nodes of the level with current connection state."""
        nodes_list = []
        for n in self._level.node_config.nodes:
            nodes_list.append({"id": n.node_id,
                               "x": n.grid_point[0].position_x,
                               "y": n.grid_point[0].position_y,
                               "type": n.node_type.name,
                               "max_connections": n.node_type.max_connections,
                               "current_connections": n.current_connections
                               }
                              )
        return nodes_list

    @Property(int, notify=budget_changed)
    def current_budget(self) -> int:
        """Current available budget for placing bridges."""
        return self._game_session.current_budget

    @Property(str, notify=time_updated)
    def elapsed_time(self) -> str:
        """Elapsed game time in mm:ss format."""
        return self._format_time(self._elapsed_seconds)

    @Property(str, notify=bridge_type_changed)
    def selected_bridge_type(self) -> str:
        """Get the currently selected bridge type name.

        Returns:
            Name of the selected bridge type, or empty string if none selected.
        """
        if self._selected_bridge_type is None:
            return ""
        return self._selected_bridge_type.name

    # === Slots ===
    @Slot()
    def pause_timer(self) -> None:
        """Pause the timer without resetting elapsed time."""
        self._timer.stop()

    @Slot()
    def resume_timer(self) -> None:
        """Resume the paused timer without resetting elapsed time."""
        self._timer.start(1000)

    @Slot()
    def request_navigate_to_main_menu(self) -> None:
        """Request navigation to main menu with confirmation dialog."""
        self.pause_timer()
        self.confirm_navigation.emit("main_menu")

    @Slot()
    def request_navigate_to_level_selection(self) -> None:
        """Request navigation to level selection menu with confirmation dialog."""
        self.pause_timer()
        self.confirm_navigation.emit("level_selection")

    @Slot()
    def reset_level(self) -> None:
        """Reset the level to initial state."""
        self._game_session = GameSession(self._player, self._level)

        # Timer reset
        self.pause_timer()
        self._elapsed_seconds = 0
        self.resume_timer()

        # Signals
        self.game_reset.emit()
        self.nodes_changed.emit()
        self.budget_changed.emit(self._game_session.current_budget)

    @Slot()
    def validate_solution(self) -> None:
        """Validate if the level is completed and calculate scores."""
        self.pause_timer()
        self._game_session.is_it_solved()
        if self._game_session.network.is_solved:
            self._game_session.calculate_redundancy_score()
            self._game_session.calculate_performance()
            self._db_service.save_completed_level(self._player.player_id,
                                                  self._level.level_id,
                                                  self._elapsed_seconds,
                                                  self._game_session.network.redundancy_score,
                                                  self._game_session.network.performance_score
                                                  )
            self.level_completed.emit(self._game_session.network.redundancy_score,
                                      self._game_session.network.performance_score,
                                      self._format_time(self._elapsed_seconds)
                                      )
        else:
            self.resume_timer()
            self.error_occurred.emit("Level is not completed")

    @Slot(str)
    def set_selected_bridge_type(self, bridge_type_str: str) -> None:
        """Set the currently selected bridge type for placement.

        Args:
            bridge_type_str: Name of the bridge type (e.g., 'FIBER', 'ETHERNET').

        Emits:
            bridge_type_changed: When a valid bridge type is selected.
            error_occurred: When an invalid bridge type string is provided.
        """
        try:
            self._selected_bridge_type = BridgeType[bridge_type_str]
            self.bridge_type_changed.emit()
        except KeyError:
            self.error_occurred.emit(f"Invalid bridge type: {bridge_type_str}")

    @Slot(int, list, int)
    def place_bridge_vm(self, from_node_id: int, grid_points_id: list, to_node_id: int) -> None:
        """Place a bridge between two nodes using the selected bridge type.

        Args:
            from_node_id: ID of the starting node
            grid_points_id: List of GridPoint IDs the bridge passes through (can be empty)
            to_node_id: ID of the ending node

        Emits:
            bridge_placed: When bridge is successfully placed
            budget_changed: With updated budget after placement
            error_occurred: When validation fails or placement fails

        Raises:
            None (all errors handled via error_occurred signal)
        """

        # Input validation
        node_ids_list = []
        for n in self._level.node_config.nodes:
            node_ids_list.append(n.node_id)

        # from_node_id
        if from_node_id not in node_ids_list:
            self.error_occurred.emit(f"from_node_id {from_node_id} not found in list of node_ids")
            return

        # to_node_id
        if to_node_id not in node_ids_list:
            self.error_occurred.emit(f"to_node_id {to_node_id} not found in list of node_ids")
            return

        # grid_points_id
        all_grid_points_id_list = []
        for g in self._level.game_board:
            all_grid_points_id_list.append(g.grid_point_id)

        for g_id in grid_points_id:
            if g_id not in all_grid_points_id_list:
                self.error_occurred.emit(f"grid_point_id {g_id} not found in list of all_grid_points_id")
                return

        # is BridgeType selected?
        if self._selected_bridge_type is None:
            self.error_occurred.emit("BridgeType is not selected")
            return

        # turn ID's to instances
        from_node = None
        to_node = None
        grid_points: list = []

        for n in self._level.node_config.nodes:
            if n.node_id == from_node_id:
                from_node = n
            if n.node_id == to_node_id:
                to_node = n
            if from_node is not None and to_node is not None:
                break

        for g_id in grid_points_id:
            for gp in self._level.game_board:
                if gp.grid_point_id == g_id:
                    grid_points.append(gp)
                    break

        # place Bridge
        try:
            self._game_session.place_bridge(from_node, grid_points, to_node, self._selected_bridge_type)
            self.bridge_placed.emit()
            self.budget_changed.emit(self._game_session.current_budget)
            self.nodes_changed.emit()

        except Exception as e:
            self.error_occurred.emit(f"Failed to place bridge: {str(e)}")

    @Slot(int)
    def remove_bridge(self, bridge_id: int) -> None:
        """Remove a bridge from the network and refund its cost.

        Args:
            bridge_id: ID of the bridge to remove

        Emits:
            bridge_removed: When bridge is successfully removed
            budget_changed: With updated budget after refund
            nodes_changed: When node connections are updated
            error_occurred: When bridge_id not found or removal fails
        """

        # Input validation
        bridge_ids_list = []
        for b in self._game_session.network.bridges:
            bridge_ids_list.append(b.bridge_id)
        if bridge_id not in bridge_ids_list:
            self.error_occurred.emit(f"Bridge with ID {bridge_id} not found in network")
            return

        # remove bridge
        bridge = None
        for b in self._game_session.network.bridges:
            if b.bridge_id == bridge_id:
                bridge = b
                break
        try:
            self._game_session.remove_bridge(bridge)
            self.bridge_removed.emit()
            self.budget_changed.emit(self._game_session.current_budget)
            self.nodes_changed.emit()

        except Exception as e:
            self.error_occurred.emit(f"Failed to remove bridge: {str(e)}")

    # === Methods ===
    def _on_timer_tick(self) -> None:
        """Called every second to update elapsed time."""
        self._elapsed_seconds += 1
        self.time_updated.emit(self.elapsed_time)

    def _format_time(self, seconds: int) -> str:
        """Convert seconds to mm:ss format (e.g., 125 → 02:05)."""
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes:02d}:{remaining_seconds:02d}"
