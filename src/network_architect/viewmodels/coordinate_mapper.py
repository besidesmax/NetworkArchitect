"""Coordinate transformation between model grid and screen pixels."""

from typing import Tuple

from network_architect.models.grid_point import GridPoint

# Constants for default rendering configuration
DEFAULT_CELL_SIZE = 50  # Pixels per grid cell
DEFAULT_OFFSET_X = 20  # Left margin in pixels
DEFAULT_OFFSET_Y = 20  # Top margin in pixels


class CoordinateMapper:
    """
    Transforms between GridPoint model coordinates and screen pixels.

    Purpose:
        - Decouples game logic (grid indices) from GUI rendering (pixels)
        - Enables different cell sizes/offsets per level
        - Single source of truth for coordinate transformation
    """

    def __init__(
            self,
            cell_size: int = DEFAULT_CELL_SIZE,
            offset_x: int = DEFAULT_OFFSET_X,
            offset_y: int = DEFAULT_OFFSET_Y
    ):
        """
        Initialize coordinate transformer with rendering configuration.

        Args:
            cell_size: Width/height of each grid cell in pixels. Default: 50.
            offset_x: Left margin offset in pixels. Default: 20.
            offset_y: Top margin offset in pixels. Default: 20.

        Raises:
            ValueError: If any parameter is negative.
        """
        if cell_size <= 0:
            raise ValueError("cell_size must be positive")
        if offset_x < 0:
            raise ValueError("offset_x must be non-negative")
        if offset_y < 0:
            raise ValueError("offset_y must be non-negative")

        self.cell_size = cell_size
        self.offset_x = offset_x
        self.offset_y = offset_y

    def grid_point_to_screen(self, grid_point: GridPoint) -> Tuple[int, int]:
        """
        Convert GridPoint to screen pixel coordinates.

        Args:
            grid_point: GridPoint model object with position_x/position_y

        Returns:
            (screen_x, screen_y) in pixels for View rendering
        """
        screen_x = grid_point.position_x * self.cell_size + self.offset_x
        screen_y = grid_point.position_y * self.cell_size + self.offset_y
        return screen_x, screen_y

    def screen_to_model(self, pixel_x: int, pixel_y: int) -> Tuple[int, int]:
        """
        Convert screen click to grid coordinates.

        Args:
            pixel_x: Click X position in pixels
            pixel_y: Click Y position in pixels

        Returns:
            Tuple of (grid_x, grid_y) logical coordinates
        """
        grid_x = (pixel_x - self.offset_x) // self.cell_size
        grid_y = (pixel_y - self.offset_y) // self.cell_size
        return grid_x, grid_y

    def screen_to_grid_point(self, pixel_x: int, pixel_y: int, grid_points_list: list[GridPoint]) -> GridPoint | None:
        """
        Convert screen click to existing GridPoint object.

        Args:
            pixel_x: Click X position in pixels
            pixel_y: Click Y position in pixels
            grid_points_list: List of all GridPoints

        Returns:
            GridPoint object at that position, or None if not found

        """
        # 1. Convert pixels to grid coordinates
        grid_x, grid_y = self.screen_to_model(pixel_x, pixel_y)

        # 2. Find existing GridPoint at that position
        for gp in grid_points_list:
            if gp.position_x == grid_x and gp.position_y == grid_y:
                return gp

        # 3. No GridPoint exists at this position
        return None

    def transform_path(self, grid_points: list[GridPoint]) -> list[Tuple[int, int]]:
        """
        Convert list of GridPoints to screen pixel coordinates for path rendering.

        Use this method to transform bridge paths for GUI drawing.

        Args:
            grid_points: List of GridPoint objects forming a path (e.g., bridge).

        Returns:
            List of (screen_x, screen_y) tuples in same order as input.
        """
        return [
            self.grid_point_to_screen(gp)
            for gp in grid_points
        ]
