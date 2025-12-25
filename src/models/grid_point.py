class GridPoint:
    """Represents a GridPoint on the board."""

    all_instances: list['GridPoint'] = []
    id_counter = 0

    def __init__(self, x: int, y: int):
        """Initialize a GridPoint with its board position.

        Args:
            x (int): X coordinate of the GridPoint on the board.
            y (int): Y coordinate of the GridPoint on the board.
        """
        self.grid_point_id = GridPoint.id_counter
        GridPoint.id_counter += 1
        self.position_x = x
        self.position_y = y
        self.used = False
        # Register every created GridPoint instance globally
        GridPoint.all_instances.append(self)

    def reset_all_grid_point() -> None:
        # TODO solve Problem that with this function, also used Grid that used by Nodes are reset to use = False
        for grid_point in GridPoint.all_instances:
            grid_point.used = False



