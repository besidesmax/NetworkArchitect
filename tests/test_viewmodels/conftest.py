from unittest.mock import Mock

import pytest

from PySide6.QtWidgets import QApplication

from models.difficulty import Difficulty
from models.grid_point import GridPoint
from models.level import Level
from models.node import Node
from models.player import Player


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for all tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def mock_db_service():
    """Create a fully configured mock DatabaseService."""
    mock_service = Mock()

    mock_player = Mock(spec=Player)
    mock_player.player_id = 1
    mock_player.name = "TestPlayer"
    mock_service.get_player_by_id.return_value = mock_player

    mock_level = Mock(spec=Level)
    mock_level.level_id = 1
    mock_level.difficulty = Difficulty.LIGHT
    mock_level.start_budget = 1000

    gridpoint1 = Mock(spec=GridPoint)
    gridpoint1.grid_point_id = 1
    gridpoint1.position_x = 100
    gridpoint1.position_y = 200

    gridpoint2 = Mock(spec=GridPoint)
    gridpoint2.grid_point_id = 2
    gridpoint2.position_x = 300
    gridpoint2.position_y = 400

    mock_level.game_board = [gridpoint1, gridpoint2]

    node1 = Mock(spec=Node)
    node1.node_id = 1
    node1.grid_point = [gridpoint1]
    node1.node_type = Mock()
    node1.node_type.name = "SERVER"
    node1.node_type.max_connections = 4
    node1.current_connections = 0

    node2 = Mock(spec=Node)
    node2.node_id = 2
    node2.grid_point = [gridpoint2]
    node2.node_type = Mock()
    node2.node_type.name = "CLIENT"
    node2.node_type.max_connections = 2
    node2.current_connections = 0

    mock_level.node_config = Mock()
    mock_level.node_config.nodes = [node1, node2]

    mock_service.get_level.return_value = mock_level

    mock_level_1 = Mock(spec=Level)
    mock_level_1.level_id = 1

    mock_level_2 = Mock(spec=Level)
    mock_level_2.level_id = 2

    mock_service.get_all_levels.return_value = [mock_level_1, mock_level_2]

    return mock_service
