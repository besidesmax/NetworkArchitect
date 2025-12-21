class GridPoint:
    """Represents a GridPoint on the board."""

    def __init__(self, grid_point_id: int, x: int, y: int):
        """Initialize a GridPoint with position

        Args:
            grid_point_id: Unique identifier of the GridPoint on the board.
            x: X coordinate of the GridPoint on the board.
            y: Y coordinate of the GridPoint on the board.
        """
        self.grid_point_id = grid_point_id
        self.position_x = x
        self.position_y = y

