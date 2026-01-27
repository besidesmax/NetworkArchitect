from PySide6.QtCore import QObject, Signal, Property, Slot
from typing import List, Dict, Any

from models.database_service import DatabaseService


class LevelSelectionViewModel(QObject):
    """
    Manages level selection for gameplay.

    Loads all available levels from database and handles level selection.
    Emits signals to notify view of level list changes and selected level.
    """

    # Signals
    levels_changed = Signal()
    level_selected = Signal(int)  # level_id
    error_occurred = Signal(str)

    def __init__(self, db_service: DatabaseService) -> None:
        """
        Initialize with database service dependency injection.

        Args:
            db_service: Persistence layer for loading levels.
        """
        super().__init__()
        self._db_service = db_service
        self._levels: List[Dict[str, Any]] = []
        self._load_levels()

    @Property(list, notify=levels_changed)
    def levels(self) -> List[Dict[str, Any]]:
        """
        Get all available levels for selection screen.

        Returns:
            List of dictionaries with level metadata:
            [
                {
                    "id": 1,
                    "difficulty": "EASY",
                    "target_performance_score": 100,
                    "target_redundancy_score": 50,
                    "start_budget": 1000
                },
                ...
            ]
        """
        return self._levels

    @Slot(int)
    def select_level(self, level_id: int) -> None:
        """
        Select a level and emit selection signal.

        Args:
            level_id: Database ID of the level to select.

        Emits:
            level_selected(level_id) on success
            error_occurred(message) on failure
        """
        try:
            if level_id <= 0:
                raise ValueError("Level ID must be positive integer")

            # Validate that level exists
            level = self._db_service.get_level(level_id)

            if not level:
                raise ValueError(f"Level ID {level_id} not found")

            # Emit selection signal
            self.level_selected.emit(level_id)

        except Exception as e:
            self.error_occurred.emit(str(e))

    def _load_levels(self) -> None:
        """
        Load all levels from database and convert to UI format.

        Called in __init__ to populate levels property.
        """
        try:
            db_levels = self._db_service.get_all_levels()

            self._levels = [
                {
                    "id": level.level_id,
                    "difficulty": level.difficulty.name,
                    "target_performance_score": level.target_performance_score,
                    "target_redundancy_score": level.target_redundancy_score,
                    "start_budget": level.start_budget
                }
                for level in db_levels
            ]

            self.levels_changed.emit()

        except Exception as e:
            self.error_occurred.emit(f"Failed to load levels: {str(e)}")
