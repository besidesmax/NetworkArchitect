class GridPoint:
    """Represents a GridPoint on the board."""

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
