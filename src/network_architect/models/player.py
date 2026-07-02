class Player:
    """Represents a player profile in the game."""

    def __init__(self, name: str) -> None:
        """Create a new player with a unique ID and display name.

        Args:
            name: Name shown in the UI
        """
        # Assign a unique ID to this player instance.
        self.player_id = None  # Will be set by DataBaseService
        self.name = name
