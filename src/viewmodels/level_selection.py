from PySide6.QtCore import QObject, Signal, Property, Slot
from typing import List, Dict, Any
from models.database_service import DatabaseService


class LevelSelectionViewModel(QObject):
    """
    Manages level selection for gameplay.

    Loads all available levels from database and handles level selection.
    Emits signals to notify view of level list changes and selected level.
    """
    # Signals for view notifications
    players_loaded = Signal()
    player_created = Signal()
    unlocked_levels_loaded = Signal()
    player_level_selected = Signal()
    error_occurred = Signal(str)

    def __init__(self, db_service: DatabaseService):
        super().__init__()
        self._db_service = db_service
        self._players_list: list = []
        self._unlocked_levels_list: list = []
        self._selected_player_u_level: dict = {}

    # === PROPERTIES ===
    @Property(list, notify=players_loaded)
    def players_list(self) -> List[Dict[str, Any]]:
        """List of all players as dicts with 'id' and 'name' keys."""
        return self._players_list

    @Property(list, notify=unlocked_levels_loaded)
    def unlocked_levels_list(self) -> List[Dict[str, Any]]:
        """List of unlocked levels as dicts with 'level_id' and 'difficulty' keys."""
        return self._unlocked_levels_list

    # === SLOTS ===
    @Slot()
    def load_players_list(self):
        """
        Load all players from database for player selection dropdown.

        Emits error_occurred signal if no players exist in database.
        """
        try:
            players = self._db_service.get_all_players()

            if not players:
                # No players in database - inform user to create one
                self._players_list = []
                self.error_occurred.emit("No players found. Please create a new player.")
                self.players_loaded.emit()
                return

            # Convert Player objects to dicts for View binding
            self._players_list = []
            for player in players:
                self._players_list.append({"id": player.player_id, "name": player.name})
            self.players_loaded.emit()

        except Exception as e:
            # Database error or unexpected exception
            self._players_list = []
            self.error_occurred.emit(f"Failed to load players: {str(e)}")

    @Slot(int)
    def load_unlocked_levels_list(self, player_id: int):
        """
        Load all unlocked levels for selected player.

        Includes completed levels and next unlocked level (sequential logic).
        Level 1 is always unlocked.

        Args:
            player_id: ID of player to load levels for.
        """
        try:
            unlocked_levels = self._db_service.get_unlocked_levels_by_player(player_id)

            if not unlocked_levels:
                self._unlocked_levels_list = []
                self.error_occurred.emit("No levels available. Please check database.")
                self.unlocked_levels_loaded.emit()
                return

            self._unlocked_levels_list = unlocked_levels
            self.unlocked_levels_loaded.emit()

        except ValueError as e:
            # Player not found (raised by get_player_by_id in DatabaseService)
            self._unlocked_levels_list = []
            self.error_occurred.emit(f"Invalid player: {str(e)}")
        except Exception as e:
            # Unexpected error (database connection, corruption, etc.)
            self._unlocked_levels_list = []
            self.error_occurred.emit(f"Failed to load levels: {str(e)}")
