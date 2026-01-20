from models.level import Level
from models.difficulty import Difficulty


def test_create_level() -> None:
    """Level constructor should set difficulty, grid size and create a full board."""
    # Arrange & Act: create a level with LIGHT difficulty.
    level1 = Level(Difficulty.LIGHT, 500, 500)

    # Assert: difficulty and grid dimensions are taken from the Difficulty enum.
    assert level1.difficulty is Difficulty.LIGHT
    assert level1.grid_height is Difficulty.LIGHT.height
    assert level1.grid_width is Difficulty.LIGHT.width

    # Assert: game_board contains one GridPoint for each grid cell.
    assert len(level1.game_board) == level1.grid_width * level1.grid_height
