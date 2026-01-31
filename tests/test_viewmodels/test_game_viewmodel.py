import pytest
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication

from viewmodels.game_viewmodel import GameViewModel
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


class TestGameViewModelInit:
    """Test GameViewModel initialization."""

    @pytest.fixture
    def mock_db_service(self):
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

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_init_loads_player_from_database(
            self,
            _mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that __init__ loads player by ID from database."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)

        mock_db_service.get_player_by_id.assert_called_once_with(player_id)
        assert viewmodel._player.player_id == 1
        assert viewmodel._player.name == "TestPlayer"

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_init_loads_level_from_database(
            self,
            _mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that __init__ loads level by ID from database."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)

        mock_db_service.get_level.assert_called_once_with(level_id)
        assert viewmodel._level.level_id == 1
        assert viewmodel._level.difficulty == Difficulty.LIGHT

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_init_creates_game_session(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that __init__ creates GameSession with player and level."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)

        mock_game_session_class.assert_called_once_with(
            viewmodel._player,
            viewmodel._level
        )
        assert viewmodel._game_session is not None

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_init_transforms_game_board_to_dict_list(
            self,
            _mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that __init__ transforms GridPoints to list of dicts."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)

        assert len(viewmodel._game_board) == 2
        assert viewmodel._game_board[0] == {"id": 1, "x": 100, "y": 200}
        assert viewmodel._game_board[1] == {"id": 2, "x": 300, "y": 400}

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_init_starts_timer(
            self,
            _mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that __init__ starts the timer."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)

        assert viewmodel._timer.isActive()
        assert viewmodel._timer.interval() == 1000

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_init_sets_elapsed_seconds_to_zero(
            self,
            _mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that __init__ initializes elapsed_seconds to 0."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)

        assert viewmodel._elapsed_seconds == 0
