from PySide6.QtCore import QObject, Signal, Property, Slot
from typing import List
from models.database_service import DatabaseService


class PlayerSelectionViewModel(QObject):
    """Manages player list and selection for main menu flow."""
    players_changed = Signal()
    player_selected = Signal(int)

    def __init__(self, db_service: DatabaseService) -> None:
        """
        Initialize with database service dependency injection.

        Args:
            db_service: Persistence layer for player CRUD operations.
        """
        super().__init__()
        self._db_service = db_service

    @Property(list, notify=players_changed)
    def players(self) -> List[dict]:
        return [{"id": p.player_id, "name": p.name}
                for p in self._db_service.get_all_players()]

    @Slot(str)
    def create_player(self, name: str):
        if name.strip():
            self._db_service.create_player(name)
            self.players_changed.emit()

    @Slot(int)
    def select_player(self, player_id: int):
        self.player_selected.emit(player_id)
