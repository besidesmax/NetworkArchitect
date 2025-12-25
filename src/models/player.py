class Player:
    """Represents a player profile in the game."""
    id_counter = 0  # Simple in-memory counter to assign unique Player IDs.

    def __init__(self, name: str) -> None:
        """Create a new player with a unique ID and display name.

        Args:
            name: Name shown in the UI
        """
        # Assign a unique ID to this player instance.
        self.player_id = Player.id_counter
        Player.id_counter += 1

        self.name = name
