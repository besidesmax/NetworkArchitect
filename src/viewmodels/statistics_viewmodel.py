"""ViewModel for statistics screens in Network Architect game."""
from PySide6.QtCore import QObject, Slot, Signal, Property

from models.database_service import DatabaseService


class StatisticsViewModel(QObject):
    """
    ViewModel for player and level statistics views.

    Provides data binding for:
    - Player statistics (levels completed per player)
    - Level statistics (players who completed each level)
    - Dropdown data for player/level selection
    """
    # Signals for view notifications
    available_players_changed = Signal()
    available_levels_changed = Signal()
    player_statistics_loaded = Signal()
    level_statistics_loaded = Signal()

    def __init__(self, db_service: DatabaseService):
        """
        Initialize ViewModel with DatabaseService dependency.

        Args:
            db_service: Database service for loading player/level data.
        """
        super().__init__()
        self._db_service = db_service
        self._player_statistics = []
        self._level_statistics = []
        self._available_players = []
        self._available_levels = []

    # === PROPERTIES ===
    @Property(list, notify=available_players_changed)
    def available_players(self) -> list:
        """List of available players for dropdown selection."""
        return self._available_players

    @Property(list, notify=available_levels_changed)
    def available_levels(self) -> list:
        """List of available levels for dropdown selection."""
        return self._available_levels

    @Property(list, notify=player_statistics_loaded)
    def player_statistics(self) -> list:
        """List of all levels which a player completed."""
        return self._player_statistics

    @Property(list, notify=level_statistics_loaded)
    def level_statistics(self) -> list:
        """List of all players which completed a level."""
        return self._level_statistics

    # === SLOTS ===
    @Slot()
    def load_available_players(self):
        """Load all players from database for dropdown."""

        players = self._db_service.get_all_players()
        self._available_players = []
        for player in players:
            self._available_players.append({"id": player.player_id, "name": player.name})

        self.available_players_changed.emit()

    @Slot()
    def load_available_levels(self):
        """Load all levels from database for dropdown."""
        levels = self._db_service.get_all_levels()
        self._available_levels = []
        for level in levels:
            self._available_levels.append({"id": level.level_id, "difficulty": level.difficulty.display_name})

        self.available_levels_changed.emit()

    @Slot(int)
    def load_player_statistics(self, player_id: int):
        """Load completed levels for specific player from database."""
        player_statistics = self._db_service.get_player_completed_levels(player_id)
        self._player_statistics = player_statistics
        self.player_statistics_loaded.emit()

    @Slot(int)
    def load_level_statistics(self, level_id: int):
        """Load completed players for specific level from database."""
        level_statistics = self._db_service.get_level_completed_by_players(level_id)
        self._level_statistics = level_statistics
        self.level_statistics_loaded.emit()
