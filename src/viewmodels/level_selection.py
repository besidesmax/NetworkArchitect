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
        self._selected_player_and_level: dict = {}
        self._new_player: list = []

    # === PROPERTIES ===
    @Property(list, notify=players_loaded)
    def players_list(self) -> List[Dict[str, Any]]:
        """List of all players as dicts with 'id' and 'name' keys."""
        return self._players_list

    @Property(list, notify=unlocked_levels_loaded)
    def unlocked_levels_list(self) -> List[Dict[str, Any]]:
        """List of unlocked levels as dicts with 'level_id' and 'difficulty' keys."""
        return self._unlocked_levels_list

    @Property(list, notify=player_created)
    def new_player(self) -> List[Dict[str, Any]]:
        """new player that is created"""
        return self._new_player

    @Property(dict, notify=player_level_selected)
    def level_and_player(self) -> Dict[str, Any]:
        """selected Player and Level for new game"""
        return self._selected_player_and_level

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

    @Slot(str)
    def create_player(self, name: str):
        """
        Creates a new player and emits player_created or error_occurred signal.

        Args:
            name (str): Player name (2-20 characters, must be unique).
        """
        try:
            new_player = self._db_service.create_player(name)
            self._new_player = []
            self._new_player = [{"id": new_player.player_id, "name": new_player.name}]
            self.player_created.emit()

        except ValueError as e:
            self.error_occurred.emit(f"Failed to create player: {str(e)}")

    @Slot(int, int)
    def select_level_and_player(self, player_id: int, level_id: int):
        """
        Validates and stores selected player and level for game start.

        Args:
            player_id (int): ID of selected player.
            level_id (int): ID of selected level.

        Emits:
            player_level_selected: When valid selection is stored.
            error_occurred: When validation fails (empty IDs or not found in database).

        Returns:
            None
        """
        # Validate player_id is not None
        if player_id is None:
            self.error_occurred.emit("player_id is empty")
            return
        # Validate level_id is not None
        if level_id is None:
            self.error_occurred.emit("level_id is empty")
            return
        # Verify player exists in database
        try:
            self._db_service.get_player_by_id(player_id)
        except ValueError as e:
            self.error_occurred.emit(f"Failed to load player: {str(e)}")
            return
        # Verify level exists in database
        try:
            self._db_service.get_level(level_id)
        except ValueError as e:
            self.error_occurred.emit(f"Failed to load level: {str(e)}")
            return

        # Store validated selection
        self._selected_player_and_level = {"player_id": player_id, "level_id": level_id}
        self.player_level_selected.emit()
