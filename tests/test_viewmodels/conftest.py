import pytest
from unittest.mock import Mock
from PySide6.QtWidgets import QApplication

from models.player import Player
from models.level import Level
from models.difficulty import Difficulty
from models.grid_point import GridPoint


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for all tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def mock_db_service():
    """Create mock DatabaseService."""
    mock_service = Mock()

    mock_player = Mock(spec=Player)
    mock_player.player_id = 1
    mock_player.name = "TestPlayer"
    mock_service.get_player_by_id.return_value = mock_player

    mock_level = Mock(spec=Level)
    mock_level.level_id = 1
    mock_level.difficulty = Difficulty.LIGHT
    mock_level.start_budget = 1000

    grid_point_1 = Mock(spec=GridPoint)
    grid_point_1.grid_point_id = 1
    grid_point_1.position_x = 100
    grid_point_1.position_y = 200

    grid_point_2 = Mock(spec=GridPoint)
    grid_point_2.grid_point_id = 2
    grid_point_2.position_x = 300
    grid_point_2.position_y = 400

    mock_level.game_board = [grid_point_1, grid_point_2]
    mock_level.node_config = Mock()
    mock_level.node_config.nodes = []

    mock_service.get_level.return_value = mock_level

    return mock_service
