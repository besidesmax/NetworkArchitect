from unittest.mock import patch

from network_architect.viewmodels.game_viewmodel import GameViewModel


class TestGameViewModelValidateSolutionSolved:
    """Test validate_solution when level is solved."""

    @patch('network_architect.viewmodels.game_viewmodel.GameSession')
    def test_validate_solution_pauses_timer_when_solved(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that validate_solution pauses timer when level is solved."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        mock_game_session = viewmodel._game_session
        mock_game_session.network.is_solved = True

        assert viewmodel._timer.isActive()

        viewmodel.validate_solution()

        assert not viewmodel._timer.isActive()

    @patch('network_architect.viewmodels.game_viewmodel.GameSession')
    def test_validate_solution_calls_is_it_solved(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that validate_solution calls is_it_solved method."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        mock_game_session = viewmodel._game_session
        mock_game_session.network.is_solved = True

        viewmodel.validate_solution()

        mock_game_session.is_it_solved.assert_called_once()

    @patch('network_architect.viewmodels.game_viewmodel.GameSession')
    def test_validate_solution_calculates_scores_when_solved(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that validate_solution calculates scores when solved."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        mock_game_session = viewmodel._game_session
        mock_game_session.network.is_solved = True

        viewmodel.validate_solution()

        mock_game_session.calculate_redundancy_score.assert_called_once()
        mock_game_session.calculate_performance.assert_called_once()

    @patch('network_architect.viewmodels.game_viewmodel.GameSession')
    def test_validate_solution_saves_to_database_when_solved(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that validate_solution saves to database with correct parameters."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        mock_game_session = viewmodel._game_session
        mock_game_session.network.is_solved = True
        mock_game_session.network.redundancy_score = 85
        mock_game_session.network.performance_score = 92

        viewmodel._elapsed_seconds = 120

        viewmodel.validate_solution()

        mock_db_service.save_completed_level.assert_called_once_with(
            player_id,
            level_id,
            120,
            85,
            92
        )

    @patch('network_architect.viewmodels.game_viewmodel.GameSession')
    def test_validate_solution_emits_level_completed_signal(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp,
            qtbot
    ):
        """Test that validate_solution emits level_completed signal with scores."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        mock_game_session = viewmodel._game_session
        mock_game_session.network.is_solved = True
        mock_game_session.network.redundancy_score = 85
        mock_game_session.network.performance_score = 92

        viewmodel._elapsed_seconds = 125

        with qtbot.waitSignal(viewmodel.level_completed, timeout=1000) as blocker:
            viewmodel.validate_solution()

        assert blocker.args == [85, 92, "02:05"]

    @patch('network_architect.viewmodels.game_viewmodel.GameSession')
    def test_validate_solution_timer_stays_stopped_when_solved(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that timer remains stopped after successful validation."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        mock_game_session = viewmodel._game_session
        mock_game_session.network.is_solved = True

        viewmodel.validate_solution()

        assert not viewmodel._timer.isActive()


class TestGameViewModelValidateSolutionNotSolved:
    """Test validate_solution when level is not solved."""

    @patch('network_architect.viewmodels.game_viewmodel.GameSession')
    def test_validate_solution_resumes_timer_when_not_solved(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that validate_solution resumes timer when level is not solved."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        mock_game_session = viewmodel._game_session
        mock_game_session.network.is_solved = False

        viewmodel.validate_solution()

        assert viewmodel._timer.isActive()

    @patch('network_architect.viewmodels.game_viewmodel.GameSession')
    def test_validate_solution_emits_error_when_not_solved(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp,
            qtbot
    ):
        """Test that validate_solution emits error_occurred signal when not solved."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        mock_game_session = viewmodel._game_session
        mock_game_session.network.is_solved = False

        with qtbot.waitSignal(viewmodel.error_occurred, timeout=1000) as blocker:
            viewmodel.validate_solution()

        assert blocker.args[0] == "Level is not completed"

    @patch('network_architect.viewmodels.game_viewmodel.GameSession')
    def test_validate_solution_does_not_save_to_db_when_not_solved(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that validate_solution does not save to database when not solved."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        mock_game_session = viewmodel._game_session
        mock_game_session.network.is_solved = False

        viewmodel.validate_solution()

        mock_db_service.save_completed_level.assert_not_called()

    @patch('network_architect.viewmodels.game_viewmodel.GameSession')
    def test_validate_solution_does_not_calculate_scores_when_not_solved(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that validate_solution does not calculate scores when not solved."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        mock_game_session = viewmodel._game_session
        mock_game_session.network.is_solved = False

        viewmodel.validate_solution()

        mock_game_session.calculate_redundancy_score.assert_not_called()
        mock_game_session.calculate_performance.assert_not_called()
