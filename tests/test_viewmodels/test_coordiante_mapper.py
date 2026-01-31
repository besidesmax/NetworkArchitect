"""Unit tests for CoordinateMapper coordinate transformation."""

import pytest

from models.grid_point import GridPoint
from viewmodels.coordinate_mapper import CoordinateMapper, DEFAULT_CELL_SIZE, DEFAULT_OFFSET_X, \
    DEFAULT_OFFSET_Y


class TestCoordinateMapperInit:
    """Test initialization and validation of CoordinateMapper."""

    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        mapper = CoordinateMapper()

        assert mapper.cell_size == DEFAULT_CELL_SIZE
        assert mapper.offset_x == DEFAULT_OFFSET_X
        assert mapper.offset_y == DEFAULT_OFFSET_Y

    def test_init_with_custom_values(self):
        """Test initialization with custom parameters."""
        mapper = CoordinateMapper(cell_size=100, offset_x=50, offset_y=30)

        assert mapper.cell_size == 100
        assert mapper.offset_x == 50
        assert mapper.offset_y == 30

    def test_init_raises_error_on_zero_cell_size(self):
        """Test that cell_size=0 raises ValueError."""
        with pytest.raises(ValueError, match="cell_size must be positive"):
            CoordinateMapper(cell_size=0)

    def test_init_raises_error_on_negative_cell_size(self):
        """Test that negative cell_size raises ValueError."""
        with pytest.raises(ValueError, match="cell_size must be positive"):
            CoordinateMapper(cell_size=-10)

    def test_init_raises_error_on_negative_offset_x(self):
        """Test that negative offset_x raises ValueError."""
        with pytest.raises(ValueError, match="offset_x must be non-negative"):
            CoordinateMapper(offset_x=-5)

    def test_init_raises_error_on_negative_offset_y(self):
        """Test that negative offset_y raises ValueError."""
        with pytest.raises(ValueError, match="offset_y must be non-negative"):
            CoordinateMapper(offset_y=-5)


class TestGridPointToScreen:
    """Test GridPoint to screen pixel coordinate transformation."""

    def test_grid_point_at_origin_with_defaults(self):
        """Test GridPoint(0,0) transforms to (20,20) with default offsets."""
        mapper = CoordinateMapper()
        grid_point = GridPoint(x=0, y=0)

        screen_x, screen_y = mapper.grid_point_to_screen(grid_point)

        assert screen_x == 20  # 0 * 50 + 20
        assert screen_y == 20  # 0 * 50 + 20

    def test_grid_point_at_2_3_with_defaults(self):
        """Test GridPoint(2,3) transforms to (120,170) with defaults."""
        mapper = CoordinateMapper()
        grid_point = GridPoint(x=2, y=3)

        screen_x, screen_y = mapper.grid_point_to_screen(grid_point)

        assert screen_x == 120  # 2 * 50 + 20
        assert screen_y == 170  # 3 * 50 + 20

    def test_grid_point_with_custom_cell_size(self):
        """Test transformation with custom cell_size=100."""
        mapper = CoordinateMapper(cell_size=100, offset_x=0, offset_y=0)
        grid_point = GridPoint(x=3, y=2)

        screen_x, screen_y = mapper.grid_point_to_screen(grid_point)

        assert screen_x == 300  # 3 * 100 + 0
        assert screen_y == 200  # 2 * 100 + 0

    def test_grid_point_with_custom_offsets(self):
        """Test transformation with custom offsets."""
        mapper = CoordinateMapper(cell_size=50, offset_x=100, offset_y=50)
        grid_point = GridPoint(x=1, y=1)

        screen_x, screen_y = mapper.grid_point_to_screen(grid_point)

        assert screen_x == 150  # 1 * 50 + 100
        assert screen_y == 100  # 1 * 50 + 50

    def test_grid_point_at_large_coordinates(self):
        """Test transformation with large grid coordinates."""
        mapper = CoordinateMapper()
        grid_point = GridPoint(x=10, y=15)

        screen_x, screen_y = mapper.grid_point_to_screen(grid_point)

        assert screen_x == 520  # 10 * 50 + 20
        assert screen_y == 770  # 15 * 50 + 20


class TestScreenToModel:
    """Test screen pixel to grid coordinate transformation."""

    def test_click_at_origin_with_defaults(self):
        """Test click at (20,20) maps to grid (0,0)."""
        mapper = CoordinateMapper()

        grid_x, grid_y = mapper.screen_to_model(20, 20)

        assert grid_x == 0
        assert grid_y == 0

    def test_click_at_120_170_with_defaults(self):
        """Test click at (120,170) maps to grid (2,3)."""
        mapper = CoordinateMapper()

        grid_x, grid_y = mapper.screen_to_model(120, 170)

        assert grid_x == 2
        assert grid_y == 3

    def test_click_within_cell_boundaries(self):
        """Test that clicks within same cell map to same grid coordinate."""
        mapper = CoordinateMapper()  # cell_size=50, offset=20

        # All clicks within first cell (20-69, 20-69) should map to (0,0)
        assert mapper.screen_to_model(20, 20) == (0, 0)
        assert mapper.screen_to_model(30, 40) == (0, 0)
        assert mapper.screen_to_model(69, 69) == (0, 0)

        # Click at (70, 70) should map to next cell (1, 1)
        assert mapper.screen_to_model(70, 70) == (1, 1)

    def test_click_with_custom_cell_size(self):
        """Test transformation with custom cell_size."""
        mapper = CoordinateMapper(cell_size=100, offset_x=0, offset_y=0)

        grid_x, grid_y = mapper.screen_to_model(250, 150)

        assert grid_x == 2  # (250 - 0) // 100
        assert grid_y == 1  # (150 - 0) // 100

    def test_click_before_offset(self):
        """Test click before offset area maps to negative grid coordinate."""
        mapper = CoordinateMapper(cell_size=50, offset_x=20, offset_y=20)

        grid_x, grid_y = mapper.screen_to_model(10, 10)

        # (10 - 20) // 50 = -10 // 50 = -1
        assert grid_x == -1
        assert grid_y == -1


class TestScreenToGridPoint:
    """Test screen click to GridPoint object lookup."""

    def test_find_grid_point_at_clicked_position(self):
        """Test finding existing GridPoint at clicked location."""
        mapper = CoordinateMapper()

        # Create GridPoints
        gp1 = GridPoint(x=0, y=0)
        gp2 = GridPoint(x=2, y=3)
        gp3 = GridPoint(x=5, y=5)
        grid_points = [gp1, gp2, gp3]

        # Click at screen position of gp2 (120, 170)
        found_gp = mapper.screen_to_grid_point(120, 170, grid_points)

        assert found_gp is gp2
        assert found_gp.position_x == 2
        assert found_gp.position_y == 3

    def test_find_grid_point_with_click_within_cell(self):
        """Test finding GridPoint with click anywhere in its cell."""
        mapper = CoordinateMapper()

        gp = GridPoint(x=1, y=1)
        grid_points = [gp]

        # Click at different positions within cell (1,1) -> screen (70-119, 70-119)
        assert mapper.screen_to_grid_point(70, 70, grid_points) is gp
        assert mapper.screen_to_grid_point(90, 100, grid_points) is gp
        assert mapper.screen_to_grid_point(119, 119, grid_points) is gp

    def test_return_none_when_no_grid_point_at_position(self):
        """Test that None is returned when no GridPoint exists at clicked cell."""
        mapper = CoordinateMapper()

        gp = GridPoint(x=0, y=0)
        grid_points = [gp]

        # Click at cell (2, 2) where no GridPoint exists
        found_gp = mapper.screen_to_grid_point(120, 120, grid_points)

        assert found_gp is None

    def test_return_none_with_empty_grid_points_list(self):
        """Test that None is returned when grid_points_list is empty."""
        mapper = CoordinateMapper()

        found_gp = mapper.screen_to_grid_point(100, 100, [])

        assert found_gp is None

    def test_find_correct_grid_point_among_many(self):
        """Test finding correct GridPoint in a list with multiple points."""
        mapper = CoordinateMapper()

        # Create 3x3 grid of GridPoints
        grid_points = [
            GridPoint(x=i, y=j)
            for i in range(3)
            for j in range(3)
        ]

        # Click at screen position (170, 120) -> grid (3, 2)
        # But we only have 0-2, so click (120, 70) -> grid (2, 1)
        found_gp = mapper.screen_to_grid_point(120, 70, grid_points)

        assert found_gp is not None
        assert found_gp.position_x == 2
        assert found_gp.position_y == 1


class TestTransformPath:
    """Test transformation of GridPoint paths to screen coordinates."""

    def test_transform_empty_path(self):
        """Test transforming empty path returns empty list."""
        mapper = CoordinateMapper()

        result = mapper.transform_path([])

        assert result == []

    def test_transform_single_grid_point(self):
        """Test transforming path with single GridPoint."""
        mapper = CoordinateMapper()
        gp = GridPoint(x=2, y=3)

        result = mapper.transform_path([gp])

        assert result == [(120, 170)]

    def test_transform_horizontal_path(self):
        """Test transforming horizontal bridge path."""
        mapper = CoordinateMapper()
        path = [
            GridPoint(x=0, y=0),
            GridPoint(x=1, y=0),
            GridPoint(x=2, y=0)
        ]

        result = mapper.transform_path(path)

        assert result == [(20, 20), (70, 20), (120, 20)]

    def test_transform_vertical_path(self):
        """Test transforming vertical bridge path."""
        mapper = CoordinateMapper()
        path = [
            GridPoint(x=1, y=0),
            GridPoint(x=1, y=1),
            GridPoint(x=1, y=2),
            GridPoint(x=1, y=3)
        ]

        result = mapper.transform_path(path)

        assert result == [(70, 20), (70, 70), (70, 120), (70, 170)]

    def test_transform_diagonal_path(self):
        """Test transforming diagonal path."""
        mapper = CoordinateMapper()
        path = [
            GridPoint(x=0, y=0),
            GridPoint(x=1, y=1),
            GridPoint(x=2, y=2)
        ]

        result = mapper.transform_path(path)

        assert result == [(20, 20), (70, 70), (120, 120)]

    def test_transform_path_with_custom_cell_size(self):
        """Test path transformation with custom cell_size."""
        mapper = CoordinateMapper(cell_size=100, offset_x=0, offset_y=0)
        path = [
            GridPoint(x=0, y=0),
            GridPoint(x=1, y=0)
        ]

        result = mapper.transform_path(path)

        assert result == [(0, 0), (100, 0)]

    def test_transform_path_preserves_order(self):
        """Test that path transformation preserves GridPoint order."""
        mapper = CoordinateMapper()
        path = [
            GridPoint(x=5, y=5),
            GridPoint(x=0, y=0),
            GridPoint(x=3, y=2)
        ]

        result = mapper.transform_path(path)

        assert result == [(270, 270), (20, 20), (170, 120)]
