from PySide6.QtCore import QObject, Signal, Property
from typing import List
from models.database_service import DatabaseService
from .view_items import NodeViewItem, BridgeViewItem


class GameViewModel(QObject):
    """MVVM ViewModel coordinating game state for Network Architect."""

    # Signals for view notifications
    level_loaded = Signal()
    bridge_placed = Signal()
    budget_changed = Signal(int)
    error_occurred = Signal(str)

    def __init__(self, db_service: DatabaseService):
        """
        Initialize ViewModel with DatabaseService dependency injection.

        Args:
            db_service: Persistence layer for loading levels/game sessions.
        """
        super().__init__()
        self._db_service = db_service

        # Private UI state collections
        self._nodes: List[NodeViewItem] = []
        self._bridges: List[BridgeViewItem] = []
        self._budget: int = 0
        self._error_message: str = ""

    @Property(int, notify=budget_changed)
    def budget(self) -> int:
        """Current game budget for status bar display."""
        return self._budget

    @budget.setter
    def budget(self, value: int) -> None:
        """Update budget value and notify connected views."""
        if self._budget != value:
            self._budget = value
            self.budget_changed.emit(value)

    @Property(list, notify=level_loaded)
    def nodes(self) -> List[NodeViewItem]:
        """UI-ready nodes for QGraphicsView rendering."""
        return self._nodes[:]

    @Property(list, notify=bridge_placed)
    def bridges(self) -> List[BridgeViewItem]:
        """UI-ready bridges for connection path visualization."""
        return self._bridges[:]

    @Property(str, notify=error_occurred)
    def error_message(self) -> str:
        """Last validation error message for dialog display."""
        return self._error_message

    @error_message.setter
    def error_message(self, value: str):
        if self._error_message != value:
            self._error_message = value
            self.error_occurred.emit(value)

    def load_level(self, level_id: int) -> None:
        """Load level from database and populate UI collections."""
        try:
            level = self._db_service.get_level(level_id)

            self._nodes = []

            for node in level.node_config.nodes:
                self._nodes.append(NodeViewItem(node_id=node.node_id,
                                                x=node.grid_point[0].position_x,
                                                y=node.grid_point[0].position_y,
                                                max_connections=node.node_type.max_connections,
                                                min_connections=node.node_type.min_connections,
                                                current_connections=node.current_connections,
                                                node_type=node.node_type.display_name
                                                )
                                   )

            self.budget = level.start_budget
            self.level_loaded.emit(level_id)

        except ValueError as e:
            self.error_message = f"Level {level_id}: {str(e)}"
            self.error_occurred.emit(self.error_message)
        except Exception as e:
            self.error_message = f"Unerwarteter Fehler: {str(e)}"
            self.error_occurred.emit(self.error_message)
