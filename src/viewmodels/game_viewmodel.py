from typing import List

from enum import Enum
from PySide6.QtCore import QObject, Signal, Property, Slot

from models.database_service import DatabaseService
from models.player import Player
from models.game_session import GameSession
from models.bridge_type import BridgeType
from models.level import Level
from models.grid_point import GridPoint
from .view_items import NodeViewItem, BridgeViewItem


class BridgeState(Enum):
    """Bridge placement state machine for GameViewModel."""
    TYPE_SELECTED = 0
    FROM_NODE_SELECTED = 1
    PATH_DRAWING = 2
    TO_NODE_SELECTED = 3


class GameViewModel(QObject):
    """MVVM ViewModel coordinating game state for Network Architect."""

    # Signals for view notifications
    level_loaded = Signal(int)  # level_id
    solution_checked = Signal(bool)  # is_solved
    bridge_placed = Signal(int, int, str)  # from_node_id, to_node_id, bridge_type
    bridge_removed = Signal(int)  # bridge_id
    budget_changed = Signal(int)  # remaining_budget
    score_changed = Signal(float, float)  # performance_score, redundancy_score
    error_occurred = Signal(str)  # error_message
    nodes_changed = Signal()  # no parameters
    time_changed = Signal(int)  # elapsed_seconds
    bridge_state_changed = Signal(int)  # BridgeState.value

    def __init__(self, db_service: DatabaseService):
        """
        Initialize ViewModel with DatabaseService dependency injection.

        Args:
            db_service: Persistence layer for loading levels/game sessions.
        """
        super().__init__()
        self._db_service = db_service
        self._player: Player | None = None
        self._session: GameSession | None = None
        self._loaded_level: Level | None = None

        # Bridge State Machine
        self.bridge_state = BridgeState.TYPE_SELECTED
        self.selected_bridge_type: BridgeType | None = None
        self.path_points: list[GridPoint] = []
        self.from_node_id: int | None = None

        # Private UI state collections
        self._nodes: List[NodeViewItem] = []
        self._bridges: List[BridgeViewItem] = []
        self._budget: int = 0
        self._is_solved = False
        self._performance_score = 0.0
        self._redundancy_score = 0.0
        self._error_message: str = ""

    # === PROPERTIES ===
    @property
    def player(self) -> Player | None:
        """Read-only player property for testing."""
        return self._player

    @Property(list, notify=nodes_changed)
    def nodes(self) -> List[NodeViewItem]:
        return self._nodes

    @nodes.setter
    def nodes(self, value: List[NodeViewItem]):
        if self._nodes != value:
            self._nodes = value
            self.nodes_changed.emit()

    @Property(list, notify=None)
    def bridges(self) -> List[BridgeViewItem]:
        """Read-only property. Use bridge_placed/bridge_removed signals for updates."""
        return self._bridges

    @Property(int, notify=budget_changed)
    def budget(self) -> int:
        return self._budget

    @budget.setter
    def budget(self, value: int):
        if self._budget != value:
            self._budget = value
            self.budget_changed.emit(value)

    @Property(bool, notify=solution_checked)
    def is_solved(self) -> bool:
        return self._is_solved

    @is_solved.setter
    def is_solved(self, value: bool):
        if self._is_solved != value:
            self._is_solved = value
            self.solution_checked.emit(value)

    @Property(float, notify=score_changed)
    def performance_score(self) -> float:
        return self._performance_score

    @performance_score.setter
    def performance_score(self, value: float):
        if self._performance_score != value:
            self._performance_score = value
            self.score_changed.emit(value, self._redundancy_score)

    @Property(float, notify=score_changed)
    def redundancy_score(self) -> float:
        return self._redundancy_score

    @redundancy_score.setter
    def redundancy_score(self, value: float):
        if self._redundancy_score != value:
            self._redundancy_score = value
            self.score_changed.emit(self._performance_score, value)

    @Property(str, notify=error_occurred)
    def error_message(self) -> str:
        return self._error_message

    @error_message.setter
    def error_message(self, value: str):
        if self._error_message != value:
            self._error_message = value
            self.error_occurred.emit(value)

    # === SLOTS ===
    @Slot(int)
    def set_player(self, player_id: int):
        """Load player by ID and store for upcoming level selection."""
        try:
            self._player = self._db_service.get_player_by_id(player_id)
        except Exception as e:
            self.error_message = str(e)

    @Slot(int)
    def load_level(self, level_id: int) -> None:
        """Load level from database."""
        try:
            # Load level from database
            level = self._db_service.get_level(level_id)

            if not level:
                raise ValueError(f"Level ID {level_id} not found")

            # Store loaded level temporarily
            self._loaded_level = level

            # Emit signal that level was loaded from DB
            self.level_loaded.emit(level_id)

        except Exception as e:
            self.error_message = str(e)

    @Slot()
    def create_game_session(self) -> None:
        """
        Create a new GameSession with stored player and loaded level.

        Emits:
            error_occurred(message) on failure

        Raises:
            ValueError: If player not set or level not loaded.
        """
        try:
            # Precondition: Player must be set
            if not self._player:
                raise ValueError("No player selected. Call set_player() first.")

            # Precondition: Level must be loaded
            if not self._loaded_level:
                raise ValueError("No level loaded. Call load_level() first.")

            # Create GameSession with player + level
            self._session = GameSession(self._player, self._loaded_level)

            # Initialize UI state with level budget
            self.budget = self._session.current_budget

            # Convert nodes to NodeViewItems for UI binding
            self._update_nodes_view()

            # Initialize bridge list as empty
            self._bridges = []

        except Exception as e:
            self.error_message = str(e)

    @Slot(int, int, str, list)
    def place_bridge(self, from_node_id: int, to_node_id: int,
                     bridge_type: str, path_points: list):
        """Places bridge with explicit path between nodes."""
        try:
            bridge_type_enum = BridgeType[bridge_type.upper()]

            grid_points = []

            # Convert path points to GridPoints
            for p in path_points:
                if isinstance(p, GridPoint):
                    grid_points.append(p)
                else:  # QPointF from QML
                    grid_points.append(GridPoint(x=int(p.x()), y=int(p.y())))

                    # Budget check
            path_cost = len(grid_points) * bridge_type_enum.cost
            if path_cost > self._budget:
                self.error_message = f"Insufficient budget"
                return

            # Get Node objects
            nodes = self._session.level.node_config.nodes
            if from_node_id >= len(nodes) or to_node_id >= len(nodes):
                self.error_message = "Invalid node IDs"
                return

            from_node = nodes[from_node_id]
            to_node = nodes[to_node_id]

            # Correct order: from_node, grid_points, to_node, bridge_type
            success = self._session.place_bridge(
                from_node,
                grid_points,  # ✅ NOW DEFINED!
                to_node,
                bridge_type_enum
            )

            if success:
                self._budget -= path_cost
                self._update_bridges_view()
                self.bridge_placed.emit(from_node_id, to_node_id, bridge_type)
            else:
                self.error_message = "Bridge placement failed"

        except Exception as e:
            self.error_message = f"Error: {str(e)}"

    @Slot(str)
    def select_bridge_type(self, bridge_type: str):
        """Step 1: Select bridge type → Enter FROM_NODE state."""
        try:
            self.selected_bridge_type = BridgeType[bridge_type.upper()]
            self.bridge_state = BridgeState.FROM_NODE_SELECTED
            self.path_points.clear()

            self.bridge_state_changed.emit(self.bridge_state.value)
            self.error_message = f"Selected {bridge_type}. Tap start node."

        except KeyError:
            self.error_message = f"Invalid bridge type: {bridge_type}"

    @Slot(int)
    def select_from_node(self, node_id: int):
        """
        Step 2/4: Player selects start node → Enter PATH_DRAWING state.

        Args:
            node_id: Index/ID of NodeViewItem in self._nodes list
        """
        # State guard
        if self.bridge_state != BridgeState.FROM_NODE_SELECTED:
            self.error_message = "Select bridge type first"
            return

        # Validate node exists
        if node_id < 0 or node_id >= len(self._nodes):
            self.error_message = f"Invalid node ID: {node_id}"
            return

        # Store start node (NO path yet!)
        self.from_node_id = node_id
        self.path_points.clear()  # Reset path for fresh drawing

        # Advance state
        self.bridge_state = BridgeState.PATH_DRAWING
        self.bridge_state_changed.emit(self.bridge_state.value)
        self.error_message = "Draw path to target node"

    @Slot('QPointF')
    def add_path_point(self, point):
        """
        Step 3/4: Player drags path → Collect intermediate points.
        Called continuously during mouse/touch drag between from_node and to_node.

        Args:
            point: QPointF from QML MouseArea onPositionChanged event
        """
        # State guard: Only accept points during path drawing
        if self.bridge_state != BridgeState.PATH_DRAWING:
            return

        # Convert QML QPointF → GridPoint model
        grid_point = GridPoint(
            x=int(point.x()),
            y=int(point.y())
        )

        # Path smoothing: Skip if too close to last point (anti-duplicate)
        if self.path_points:
            last_point = self.path_points[-1]
            distance_squared = (
                    (grid_point.position_x - last_point.position_x) ** 2 +
                    (grid_point.position_y - last_point.position_y) ** 2
            )
            if distance_squared < 25:  # 5px threshold (5^2 = 25)
                return

        # Budget validation: Check if path length exceeds budget
        if self.selected_bridge_type:
            path_cost = (len(self.path_points) + 1) * self.selected_bridge_type.cost
            if path_cost > self._budget:
                self.error_message = "Path too long for remaining budget"
                return

        # Add valid point to path
        self.path_points.append(grid_point)

    @Slot(int)
    def select_to_node(self, node_id: int):
        """
        Step 4/4: Player selects target node → Finalize bridge placement.

        Args:
            node_id: Index/ID of target NodeViewItem
        """
        # State guard
        if self.bridge_state != BridgeState.PATH_DRAWING:
            self.error_message = "No active path to finalize"
            return

        # Validate node exists
        if node_id < 0 or node_id >= len(self._nodes):
            self.error_message = f"Invalid target node: {node_id}"
            return

        # Validate different from start node
        if node_id == self.from_node_id:
            self.error_message = "Cannot connect node to itself"
            return

        # Call place_bridge with complete path
        self.place_bridge(
            self.from_node_id,
            node_id,
            self.selected_bridge_type.name,
            self.path_points
        )

        # Reset state machine to TYPE_SELECTED
        self.bridge_state = BridgeState.TYPE_SELECTED
        self.bridge_state_changed.emit(self.bridge_state.value)
        self.from_node_id = None
        self.selected_bridge_type = None

    @Slot(int)
    def remove_bridge(self, bridge_id: int) -> None:
        """
        Remove a bridge by ID and refund its cost to budget.

        Args:
            bridge_id: ID of the bridge to remove

        Emits:
            bridge_removed(bridge_id)
            budget_changed(new_budget)
        """
        try:
            # Session must exist
            if not self._session:
                self.error_message = "No active game session"
                return

            # Find bridge by ID
            bridge_to_remove = None
            for bridge in self._session.network.bridges:
                if bridge.bridge_id == bridge_id:
                    bridge_to_remove = bridge
                    break

            if not bridge_to_remove:
                self.error_message = f"Bridge {bridge_id} not found"
                return

            # Remove bridge and refund cost
            success = self._session.remove_bridge(bridge_to_remove)

            if success:
                # Update budget in ViewModel
                self.budget = self._session.current_budget

                # Update UI bridge list
                self._update_bridges_view()

                # Signal removal
                self.bridge_removed.emit(bridge_id)
            else:
                self.error_message = f"Failed to remove bridge {bridge_id}"

        except Exception as e:
            self.error_message = f"Error removing bridge: {str(e)}"

    @Slot()
    def check_solution(self) -> None:
        """
        Validate if puzzle is solved and calculate performance/redundancy scores.
        Called when player clicks 'Check Solution' button.

        Emits:
            solution_checked(is_solved: bool)
            score_changed(performance_score, redundancy_score) if solved
        """
        try:
            # Precondition: Session must exist
            if not self._session:
                self.error_message = "No active game session"
                self.solution_checked.emit(False)
                return

            # Check if puzzle is solved
            is_solved = self._session.is_it_solved()

            if is_solved:
                # Calculate performance score (GR-13)
                try:
                    perf_score = self._session.calculate_performance()
                    self.performance_score = perf_score
                except ValueError as e:
                    self.error_message = f"Performance calculation failed: {str(e)}"
                    self.performance_score = 0.0

                # Calculate redundancy score (GR-14)
                try:
                    red_score = self._session.calculate_redundancy_score()
                    self.redundancy_score = red_score
                except ValueError as e:
                    self.error_message = f"Redundancy calculation failed: {str(e)}"
                    self.redundancy_score = 0

                # Mark as solved
                self.is_solved = True
                self.error_message = "✅ Puzzle solved!"
            else:
                self.error_message = "❌ Puzzle not yet solved. Check all requirements."
                self.is_solved = False

            # Emit solution state
            self.solution_checked.emit(is_solved)

        except Exception as e:
            self.error_message = f"Solution check failed: {str(e)}"
            self.solution_checked.emit(False)

    # === HELPER METHOD ===
    def _update_nodes_view(self) -> None:
        """
        Convert Level.node_config.nodes to NodeViewItems for UI binding.
        """
        try:
            if not self._session or not self._session.level:
                raise ValueError("No active session")

            node_items = []

            for node in self._session.level.node_config.nodes:
                grid_point = node.grid_point[0]

                node_item = NodeViewItem(
                    node_id=node.node_id,
                    x=grid_point.position_x,
                    y=grid_point.position_y,
                    max_connections=node.node_type.max_connections,
                    min_connections=node.node_type.min_connections,
                    current_connections=node.current_connections,
                    node_type=node.node_type.name
                )
                node_items.append(node_item)

            self.nodes = node_items

        except Exception as e:
            self.error_message = str(e)

    # _update_bridges_view() ALTERNATIVE:
    def _update_bridges_view(self):
        """
        Convert session bridges to BridgeViewItems for QML binding.
        Called after place_bridge() to update the bridges list in UI.
        """
        try:
            if not self._session or not self._session.network:
                self._bridges = []
                return

            bridge_items = []
            for bridge in self._session.network.bridges:
                # Convert GridPoints to (x, y) tuples
                grid_points = [
                    (gp.position_x, gp.position_y)
                    for gp in bridge.path
                ]

                bridge_item = BridgeViewItem(
                    bridge_id=bridge.bridge_id,
                    from_node_id=bridge.from_node.node_id,
                    to_node_id=bridge.to_node.node_id,
                    bridge_type=bridge.bridge_type.name,
                    grid_points=grid_points
                )

                bridge_items.append(bridge_item)

            # Update backing field (triggers QML property update)
            self._bridges = bridge_items

        except Exception as e:
            self.error_message = f"Bridge view update failed: {str(e)}"
