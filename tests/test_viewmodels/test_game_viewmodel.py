import pytest
from unittest.mock import Mock

from viewmodels.game_viewmodel import GameViewModel
from models.database_service import DatabaseService
from models.player import Player
from models.level import Level
from models.difficulty import Difficulty
from models.node import Node
from models.node_type import NodeType
from models.bridge_type import BridgeType


class TestGameViewModel:

    @pytest.fixture
    def mock_db(self):
        return Mock(spec=DatabaseService)

    @pytest.fixture
    def viewmodel(self, mock_db):
        return GameViewModel(mock_db)

    def test_create_game_session_success(self, mock_db, viewmodel):
        # Arrange
        mock_player = Player(name="Test")  # ← FIX!
        mock_level = Level(Difficulty.LIGHT, 500, 500, 500)

        node1 = Node([mock_level.game_board[0]], NodeType.CLIENT)
        node2 = Node([mock_level.game_board[2]], NodeType.CLIENT)
        node3 = Node([mock_level.game_board[3]], NodeType.CLIENT)

        mock_level.node_config.nodes = [node1, node2, node3]

        mock_db.get_player_by_id.return_value = mock_player
        mock_db.get_level.return_value = mock_level

        viewmodel.set_player(1)
        viewmodel.load_level(1)

        # Act
        viewmodel.create_game_session()

        # Assert
        assert len(viewmodel.nodes) > 0
        assert viewmodel.budget > 0

    def test_create_game_session_no_player(self, mock_db, viewmodel):
        viewmodel.load_level(1)

        # Act
        viewmodel.create_game_session()

        # Assert
        assert viewmodel.error_message == "No player selected. Call set_player() first."

    def test_update_nodes_view_empty_session(self, viewmodel):
        # Arrange
        viewmodel._session = None

        # Act
        viewmodel._update_nodes_view()

        # Assert: ERROR STATE (MVVM!)
        assert viewmodel.error_message == "No active session"
        assert len(viewmodel.nodes) == 0  # Nodes leer bleiben

    def test_set_player_success(self, mock_db, viewmodel):
        mock_player = Player(name="Test")
        mock_db.get_player_by_id.return_value = mock_player

        viewmodel.set_player(1)
        assert viewmodel.player.name == "Test"
