from models.level import Level
from models.player import Player
from models.network import Network


class GameSession:
    """Represents a single game session for one player and one level."""
    id_counter = 0  # Simple in-memory counter to assign unique GameSession IDs.

    def __init__(self, player: Player, level: Level) -> None:
        """Create a new game session with an initial budget.

        Args:
            player: Player profile associated with this session.
            level: Level that is played in this session.
        """
        # Assign a unique ID to this game session instance.
        self.game_session_id = GameSession.id_counter
        GameSession.id_counter += 1
        self.player = player
        self.level = level

        # Start each session with the level's initial budget.
        self.current_budget = level.start_budget

        # Network will later hold all nodes and bridges for this level.
        self.network = Network()
