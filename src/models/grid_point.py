class GridPoint:
    """Represents a GridPoint on the board."""

    all_instances: list['GridPoint'] = []
    id_counter = 1

    def __init__(self, x: int, y: int):
        """Initialize a GridPoint with position

        Args:
            x: X coordinate of the GridPoint on the board.
            y: Y coordinate of the GridPoint on the board.
        """
        self.grid_point_id = GridPoint.id_counter
        GridPoint.id_counter += 1
        self.position_x = x
        self.position_y = y
        self.used = False
        GridPoint.all_instances.append(self)    # Auto-Registry of all GridPoints

    @staticmethod
    def reset_all_grid_point() -> None:
        # TODO solve Problem that with this function, also used Grid that used by Nodes are reset to use = False
        for grid_point in GridPoint.all_instances:
            grid_point.used = False


def create_board(width: int, height: int) -> list[GridPoint]:
    """Creates a new GameBoard
    Args:
        width (int): Number of columns (x-direction).
        height (int): Number of rows (y-direction).

    Returns:
        list[GridPoint]: All GridPoints on the board.
    """
    board: list[GridPoint] = []
    for x in range(width):
        for y in range(height):
            board.append(GridPoint(x, y))
    return board
