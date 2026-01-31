from unittest.mock import patch

from viewmodels.game_viewmodel import GameViewModel
from models.difficulty import Difficulty


class TestGameViewModelInit:
    """Test GameViewModel initialization."""

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

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_init_connects_timer_signal(
            self,
            _mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that __init__ connects timer timeout to _on_timer_tick."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)

        assert viewmodel._timer.isActive()

        viewmodel._on_timer_tick()
        assert viewmodel._elapsed_seconds == 1


class TestGameViewModelTimerSlots:
    """Test timer-related slots."""

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_pause_timer_stops_timer(
            self,
            _mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that pause_timer stops the timer."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)

        assert viewmodel._timer.isActive()

        viewmodel.pause_timer()

        assert not viewmodel._timer.isActive()

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_resume_timer_starts_timer(
            self,
            _mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that resume_timer starts the timer."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)

        viewmodel.pause_timer()
        assert not viewmodel._timer.isActive()

        viewmodel.resume_timer()

        assert viewmodel._timer.isActive()

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_pause_resume_preserves_elapsed_seconds(
            self,
            _mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that pause and resume preserve elapsed_seconds value."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)

        viewmodel._elapsed_seconds = 42

        viewmodel.pause_timer()
        viewmodel.resume_timer()

        assert viewmodel._elapsed_seconds == 42


class TestGameViewModelResetLevel:
    """Test reset_level slot."""

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_reset_level_creates_new_game_session(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that reset_level creates a new GameSession instance."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)

        initial_call_count = mock_game_session_class.call_count

        viewmodel.reset_level()

        assert mock_game_session_class.call_count == initial_call_count + 1
        mock_game_session_class.assert_called_with(
            viewmodel._player,
            viewmodel._level
        )

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_reset_level_resets_elapsed_seconds(
            self,
            _mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that reset_level resets elapsed_seconds to 0."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        viewmodel._elapsed_seconds = 99

        viewmodel.reset_level()

        assert viewmodel._elapsed_seconds == 0

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_reset_level_emits_game_reset_signal(
            self,
            _mock_game_session_class,
            mock_db_service,
            qapp,
            qtbot
    ):
        """Test that reset_level emits game_reset signal."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)

        with qtbot.waitSignal(viewmodel.game_reset, timeout=1000):
            viewmodel.reset_level()

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_reset_level_emits_nodes_changed_signal(
            self,
            _mock_game_session_class,
            mock_db_service,
            qapp,
            qtbot
    ):
        """Test that reset_level emits nodes_changed signal."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)

        with qtbot.waitSignal(viewmodel.nodes_changed, timeout=1000):
            viewmodel.reset_level()

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_reset_level_emits_budget_changed_signal(
            self,
            _mock_game_session_class,
            mock_db_service,
            qapp,
            qtbot
    ):
        """Test that reset_level emits budget_changed signal."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)

        with qtbot.waitSignal(viewmodel.budget_changed, timeout=1000):
            viewmodel.reset_level()

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_reset_level_restarts_timer(
            self,
            _mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that reset_level restarts the timer."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)

        viewmodel.pause_timer()
        assert not viewmodel._timer.isActive()

        viewmodel.reset_level()

        assert viewmodel._timer.isActive()
