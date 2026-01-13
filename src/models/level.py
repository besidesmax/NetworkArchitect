from models.difficulty import Difficulty
from models.grid_point import GridPoint
from models.node_config import NodeConfig


class Level:
    """Represents a single puzzle level with a fixed grid, node setup and scoring targets."""

    def __init__(self, difficulty: Difficulty, target_performance_score: int, target_redundancy_score: int,
                 start_budget: int):
        """Initialize a level with its difficulty, scoring target and starting budget.

        Args:
            difficulty: Difficulty setting that defines the default grid size.
            target_performance_score: Score threshold the player should reach.
            target_redundancy_score: Score threshold the player should reach.
            start_budget: Initial budget available in this level.
        """
        self.level_id = None  # Will be set by DataBaseService
        self.difficulty = difficulty
        self.grid_width = difficulty.width
        self.grid_height = difficulty.height
        # Each level owns its own node configuration and network instance.
        self.node_config = NodeConfig()
        if target_performance_score < 0:
            raise ValueError("Target Performance Score has to be higher then 0")
        self.target_performance_score = target_performance_score
        if target_redundancy_score < 0:
            raise ValueError("Target Redundancy Score has to be higher then 0")
        self.target_redundancy_score = target_redundancy_score
        if start_budget < 0:
            raise ValueError("StartBudget has to be higher then 0")
        self.start_budget = start_budget

        # Pre-create the GameBoard of GridPoints for this level.
        self.game_board: list[GridPoint] = self.create_board()

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

        # set GridPoint.id_counter to 0
        GridPoint.id_counter = 0

        return board
