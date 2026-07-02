"""Unit tests for Validator class."""

import pytest

from network_architect.models.grid_point import GridPoint
from network_architect.models.node import Node
from network_architect.models.node_type import NodeType
from network_architect.models.validator import Validator


def test_is_grid_point_used():
    """
    Test that checking an unused grid point succeeds and a used one fails.

    Verifies that:
    - Passing unused GridPoints returns None (no exception).
    - Passing a GridPoint marked as used raises a ValueError.
    """
    # Arrange (Valid Case)
    gp_1 = GridPoint(0, 1)

    # Act & Assert (Valid Case)
    assert Validator.is_grid_point_used([gp_1]) is None

    # Arrange (Invalid Case)
    gp_1.used = True

    # Act & Assert (Invalid Case)
    with pytest.raises(ValueError):
        Validator.is_grid_point_used([gp_1])


def test_is_first_grid_point_adjacent_success():
    """
    Test that all valid orthogonal directions are accepted.

    Verifies that:
    - A GridPoint located exactly one step to the right, left,
      down, or up from the Node passes validation without raising an exception.
    """
    # Arrange
    node_gp = GridPoint(1, 5)
    node = Node([node_gp], NodeType.SERVER)

    # Create orthogonally adjacent GridPoints for all four directions
    adjacent_gp_right = GridPoint(2, 5)
    adjacent_gp_left = GridPoint(0, 5)
    adjacent_gp_down = GridPoint(1, 4)
    adjacent_gp_up = GridPoint(1, 6)

    # Act & Assert
    assert Validator.is_first_grid_point_adjacent(node, [adjacent_gp_right]) is None
    assert Validator.is_first_grid_point_adjacent(node, [adjacent_gp_left]) is None
    assert Validator.is_first_grid_point_adjacent(node, [adjacent_gp_down]) is None
    assert Validator.is_first_grid_point_adjacent(node, [adjacent_gp_up]) is None


def test_is_first_grid_point_adjacent_fail():
    """
    Test that is_first_grid_point_adjacent raises ValueError for invalid inputs.

    Verifies rejection of:
    1. GridPoints with an orthogonal distance greater than 1 (too far).
    2. GridPoints placed diagonally to the Node.
    """

    # Arrange
    node_gp = GridPoint(2, 5)
    node = Node([node_gp], NodeType.SERVER)

    # Create orthogonally too far GridPoints for all four directions
    too_far_gp_right = GridPoint(4, 5)
    too_far_gp_left = GridPoint(0, 5)
    too_far_gp_down = GridPoint(2, 3)
    too_far_gp_up = GridPoint(2, 7)

    # Act & Assert 1: Distance Checks
    with pytest.raises(ValueError):
        Validator.is_first_grid_point_adjacent(node, [too_far_gp_right])
    with pytest.raises(ValueError):
        Validator.is_first_grid_point_adjacent(node, [too_far_gp_left])
    with pytest.raises(ValueError):
        Validator.is_first_grid_point_adjacent(node, [too_far_gp_down])
    with pytest.raises(ValueError):
        Validator.is_first_grid_point_adjacent(node, [too_far_gp_up])

    # Create diagonal GridPoints
    diagonal_gp_1 = GridPoint(3, 6)  # right&up
    diagonal_gp_2 = GridPoint(3, 4)  # right&down
    diagonal_gp_3 = GridPoint(1, 6)  # left&up
    diagonal_gp_4 = GridPoint(1, 4)  # left&down

    # Act & Assert 2: Diagonal Checks
    with pytest.raises(ValueError):
        Validator.is_first_grid_point_adjacent(node, [diagonal_gp_1])
    with pytest.raises(ValueError):
        Validator.is_first_grid_point_adjacent(node, [diagonal_gp_2])
    with pytest.raises(ValueError):
        Validator.is_first_grid_point_adjacent(node, [diagonal_gp_3])
    with pytest.raises(ValueError):
        Validator.is_first_grid_point_adjacent(node, [diagonal_gp_4])


def test_is_last_grid_point_adjacent_success():
    """
    Test that all valid orthogonal directions are accepted.

    Verifies that:
    - A GridPoint located exactly one step to the right, left,
      down, or up from the Node passes validation without raising an exception.
    """
    # Arrange
    node_gp = GridPoint(1, 5)
    node = Node([node_gp], NodeType.SERVER)

    # Create orthogonally adjacent GridPoints for all four directions
    adjacent_gp_right = GridPoint(2, 5)
    adjacent_gp_left = GridPoint(0, 5)
    adjacent_gp_down = GridPoint(1, 4)
    adjacent_gp_up = GridPoint(1, 6)

    # Act & Assert
    assert Validator.is_last_grid_point_adjacent(node, [adjacent_gp_right]) is None
    assert Validator.is_last_grid_point_adjacent(node, [adjacent_gp_left]) is None
    assert Validator.is_last_grid_point_adjacent(node, [adjacent_gp_down]) is None
    assert Validator.is_last_grid_point_adjacent(node, [adjacent_gp_up]) is None


def test_is_last_grid_point_adjacent_fail():
    """
    Test that is_last_grid_point_adjacent raises ValueError for invalid inputs.

    Verifies rejection of:
    1. GridPoints with an orthogonal distance greater than 1 (too far).
    2. GridPoints placed diagonally to the Node.
    """

    # Arrange
    node_gp = GridPoint(2, 5)
    node = Node([node_gp], NodeType.SERVER)

    # Create orthogonally too far GridPoints for all four directions
    too_far_gp_right = GridPoint(4, 5)
    too_far_gp_left = GridPoint(0, 5)
    too_far_gp_down = GridPoint(2, 3)
    too_far_gp_up = GridPoint(2, 7)

    # Act & Assert 1: Distance Checks
    with pytest.raises(ValueError):
        Validator.is_last_grid_point_adjacent(node, [too_far_gp_right])
    with pytest.raises(ValueError):
        Validator.is_last_grid_point_adjacent(node, [too_far_gp_left])
    with pytest.raises(ValueError):
        Validator.is_last_grid_point_adjacent(node, [too_far_gp_down])
    with pytest.raises(ValueError):
        Validator.is_last_grid_point_adjacent(node, [too_far_gp_up])

    # Create diagonal GridPoints
    diagonal_gp_1 = GridPoint(3, 6)  # right&up
    diagonal_gp_2 = GridPoint(3, 4)  # right&down
    diagonal_gp_3 = GridPoint(1, 6)  # left&up
    diagonal_gp_4 = GridPoint(1, 4)  # left&down

    # Act & Assert 2: Diagonal Checks
    with pytest.raises(ValueError):
        Validator.is_last_grid_point_adjacent(node, [diagonal_gp_1])
    with pytest.raises(ValueError):
        Validator.is_last_grid_point_adjacent(node, [diagonal_gp_2])
    with pytest.raises(ValueError):
        Validator.is_last_grid_point_adjacent(node, [diagonal_gp_3])
    with pytest.raises(ValueError):
        Validator.is_last_grid_point_adjacent(node, [diagonal_gp_4])


def test_are_grid_points_adjacent_success():
    """
    Test that sequences of orthogonally adjacent GridPoints are accepted.

    Verifies that:
    - Lists of GridPoints where each point is orthogonally adjacent
      to the next one pass validation without raising an exception.
    """
    # Arrange
    gp = GridPoint(2, 5)

    # Create orthogonally adjacent GridPoints
    gp_up = GridPoint(2, 6)
    gp_down = GridPoint(2, 4)
    gp_right = GridPoint(3, 5)
    gp_left = GridPoint(1, 5)

    # Act & Assert
    assert Validator.are_grid_points_adjacent([gp, gp_up]) is None
    assert Validator.are_grid_points_adjacent([gp, gp_down]) is None
    assert Validator.are_grid_points_adjacent([gp, gp_right]) is None
    assert Validator.are_grid_points_adjacent([gp, gp_left]) is None

    # Additional Assert: A longer valid sequence (straight line)
    gp_up_2 = GridPoint(2, 7)
    assert Validator.are_grid_points_adjacent([gp, gp_up, gp_up_2]) is None


def test_are_grid_points_adjacent_fail():
    """
    Test that are_grid_points_adjacent raises ValueError for invalid sequences.

    Verifies rejection of:
    1. GridPoints with an orthogonal distance greater than 1 (gaps in the sequence).
    2. GridPoints placed diagonally to each other.
    """
    # Arrange
    gp = GridPoint(2, 5)

    # Create GridPoints with a gap (distance > 1)
    too_far_gp_right = GridPoint(4, 5)
    too_far_gp_left = GridPoint(0, 5)
    too_far_gp_down = GridPoint(2, 3)
    too_far_gp_up = GridPoint(2, 7)

    # Act & Assert 1: Distance Checks
    with pytest.raises(ValueError):
        Validator.are_grid_points_adjacent([gp, too_far_gp_right])
    with pytest.raises(ValueError):
        Validator.are_grid_points_adjacent([gp, too_far_gp_left])
    with pytest.raises(ValueError):
        Validator.are_grid_points_adjacent([gp, too_far_gp_down])
    with pytest.raises(ValueError):
        Validator.are_grid_points_adjacent([gp, too_far_gp_up])

    # Create diagonal GridPoints
    diagonal_gp_1 = GridPoint(3, 6)  # right&up
    diagonal_gp_2 = GridPoint(3, 4)  # right&down
    diagonal_gp_3 = GridPoint(1, 6)  # left&up
    diagonal_gp_4 = GridPoint(1, 4)  # left&down

    # Act & Assert 2: Diagonal Checks
    with pytest.raises(ValueError):
        Validator.are_grid_points_adjacent([gp, diagonal_gp_1])
    with pytest.raises(ValueError):
        Validator.are_grid_points_adjacent([gp, diagonal_gp_2])
    with pytest.raises(ValueError):
        Validator.are_grid_points_adjacent([gp, diagonal_gp_3])
    with pytest.raises(ValueError):
        Validator.are_grid_points_adjacent([gp, diagonal_gp_4])
