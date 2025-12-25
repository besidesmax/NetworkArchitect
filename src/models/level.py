from models.difficulty import Difficulty
from models.grid_point import GridPoint
from models.network import Network
from models.node_config import NodeConfig


class Level:
    """Represents a single puzzle level with a fixed grid, node setup and scoring targets."""
    id_counter = 0  # Simple in-memory counter to assign unique level IDs.

    def __init__(self, difficulty: Difficulty, target_score: int, start_budget: int):
        """Initialize a level with its difficulty, scoring target and starting budget.

        Args:
            difficulty: Difficulty setting that defines the default grid size.
            target_score: Score threshold the player should reach.
            start_budget: Initial budget available in this level.
        """
        # Assign a unique ID to this level instance.
        self.level_id = Level.id_counter
        Level.id_counter += 1

        self.difficulty = difficulty
        self.grid_width = difficulty.width
        self.grid_height = difficulty.height
        # Each level owns its own node configuration and network instance.
        self.node_config = NodeConfig()
        if target_score < 0:
            raise ValueError("Target Score has to be higher then 0")
        self.target_score = target_score
        if start_budget < 0:
            raise ValueError("StartBudget has to be higher then 0")
        self.start_budget = start_budget

        # Pre-create the GameBoard of GridPoints for this level.
        self.game_board: list[GridPoint] = self.create_board()

        # Network will later hold all nodes and bridges for this level.
        self.network = Network()

    def create_board(self) -> list[GridPoint]:
        """Create a rectangular grid of GridPoints and attach it to the game board.
        Returns:
            list[GridPoint]: All GridPoints on the created board.
        """

        width = self.grid_width
        height = self.grid_height

        board: list[GridPoint] = []
        for x in range(width):
            for y in range(height):
                board.append(GridPoint(x, y))

        return board
