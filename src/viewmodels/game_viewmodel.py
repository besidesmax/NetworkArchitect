from typing import List

from enum import Enum
from PySide6.QtCore import QObject, Signal, Property, Slot

from models.database_service import DatabaseService


class GameViewModel(QObject):
    """MVVM ViewModel coordinating game state for Network Architect."""

    # Signals for view notifications
    game_session_started = Signal()

    def __init__(self, player_id: int, level_id: int, db_service: DatabaseService):
        """
        Initialize ViewModel with DatabaseService dependency injection.

        Args:
            player_id: ID of the selected player
            level_id: ID of the selected level
            db_service: Persistence layer for loading levels/game sessions.
        """
        super().__init__()
        self._db_service: int = db_service
        self._player_id = player_id
        self._level_id = level_id

    # === PROPERTIES ===


    # === SLOTS ===
    def start_game_session(self, player_id: int, level_id: int, db_service: DatabaseService):
        self._db_service
