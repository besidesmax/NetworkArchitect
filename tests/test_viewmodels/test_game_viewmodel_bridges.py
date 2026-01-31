from unittest.mock import patch, Mock

from viewmodels.game_viewmodel import GameViewModel


class TestGameViewModelPlaceBridge:
    """Test place_bridge_vm slot."""

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_place_bridge_validates_from_node_id(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that place_bridge_vm validates from_node_id exists."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        viewmodel.set_selected_bridge_type("FIBER")

        # Invalid from_node_id
        with qtbot.waitSignal(viewmodel.error_occurred, timeout=1000) as blocker:
            viewmodel.place_bridge_vm(999, [], 2)

        assert "from_node_id 999 not found" in blocker.args[0]

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_place_bridge_validates_from_node_id(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp,
            qtbot
    ):
        """Test that place_bridge_vm validates to_node_id exists."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        viewmodel.set_selected_bridge_type("FIBER")

        # Valid from_node, invalid to_node
        with qtbot.waitSignal(viewmodel.error_occurred, timeout=1000):
            viewmodel.place_bridge_vm(1, [], 999)

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_place_bridge_validates_gridpoint_ids(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp,
            qtbot
    ):
        """Test that place_bridge_vm validates all gridpoint_ids exist."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        viewmodel.set_selected_bridge_type("FIBER")

        # Valid nodes, invalid gridpoint
        with qtbot.waitSignal(viewmodel.error_occurred, timeout=1000):
            viewmodel.place_bridge_vm(1, [999], 2)

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_place_bridge_requires_bridge_type_selected(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp,
            qtbot
    ):
        """Test that place_bridge_vm requires bridge type to be selected."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        # Do NOT select bridge type

        with qtbot.waitSignal(viewmodel.error_occurred, timeout=1000) as blocker:
            viewmodel.place_bridge_vm(1, [], 2)

        assert "BridgeType is not selected" in blocker.args[0]

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_place_bridge_calls_game_session_place_bridge(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that place_bridge_vm delegates to game_session.place_bridge."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        viewmodel.set_selected_bridge_type("FIBER")
        mock_game_session = viewmodel._game_session

        viewmodel.place_bridge_vm(1, [], 2)

        # Verify place_bridge was called once
        mock_game_session.place_bridge.assert_called_once()

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_place_bridge_emits_bridge_placed_signal(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp,
            qtbot
    ):
        """Test that place_bridge_vm emits bridge_placed signal on success."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        viewmodel.set_selected_bridge_type("FIBER")

        with qtbot.waitSignal(viewmodel.bridge_placed, timeout=1000):
            viewmodel.place_bridge_vm(1, [], 2)

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_place_bridge_emits_budget_changed_signal(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp,
            qtbot
    ):
        """Test that place_bridge_vm emits budget_changed signal on success."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        viewmodel.set_selected_bridge_type("FIBER")
        mock_game_session = viewmodel._game_session
        mock_game_session.current_budget = 800

        with qtbot.waitSignal(viewmodel.budget_changed, timeout=1000) as blocker:
            viewmodel.place_bridge_vm(1, [], 2)

        assert blocker.args[0] == 800

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_place_bridge_emits_nodes_changed_signal(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp,
            qtbot
    ):
        """Test that place_bridge_vm emits nodes_changed signal on success."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        viewmodel.set_selected_bridge_type("FIBER")

        with qtbot.waitSignal(viewmodel.nodes_changed, timeout=1000):
            viewmodel.place_bridge_vm(1, [], 2)

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_place_bridge_emits_error_on_exception(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp,
            qtbot
    ):
        """Test that place_bridge_vm emits error_occurred when exception occurs."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        viewmodel.set_selected_bridge_type("FIBER")
        mock_game_session = viewmodel._game_session
        mock_game_session.place_bridge.side_effect = ValueError("Insufficient budget")

        with qtbot.waitSignal(viewmodel.error_occurred, timeout=1000) as blocker:
            viewmodel.place_bridge_vm(1, [], 2)

        assert "Failed to place bridge" in blocker.args[0]
        assert "Insufficient budget" in blocker.args[0]


class TestGameViewModelRemoveBridge:
    """Test remove_bridge slot."""

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_remove_bridge_validates_bridge_id(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp,
            qtbot
    ):
        """Test that remove_bridge validates bridge_id exists."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        mock_game_session = viewmodel._game_session
        mock_game_session.network.bridges = []  # No bridges

        with qtbot.waitSignal(viewmodel.error_occurred, timeout=1000) as blocker:
            viewmodel.remove_bridge(999)

        assert "not found" in blocker.args[0]

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_remove_bridge_calls_game_session_remove_bridge(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp
    ):
        """Test that remove_bridge delegates to game_session.remove_bridge."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        mock_game_session = viewmodel._game_session

        # Create mock bridge
        mock_bridge = Mock()
        mock_bridge.bridge_id = 1
        mock_game_session.network.bridges = [mock_bridge]

        viewmodel.remove_bridge(1)

        mock_game_session.remove_bridge.assert_called_once_with(mock_bridge)

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_remove_bridge_emits_bridge_removed_signal(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp,
            qtbot
    ):
        """Test that remove_bridge emits bridge_removed signal on success."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        mock_game_session = viewmodel._game_session

        mock_bridge = Mock()
        mock_bridge.bridge_id = 1
        mock_game_session.network.bridges = [mock_bridge]

        with qtbot.waitSignal(viewmodel.bridge_removed, timeout=1000):
            viewmodel.remove_bridge(1)

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_remove_bridge_emits_budget_changed_signal(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp,
            qtbot
    ):
        """Test that remove_bridge emits budget_changed signal with refunded budget."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        mock_game_session = viewmodel._game_session

        mock_bridge = Mock()
        mock_bridge.bridge_id = 1
        mock_game_session.network.bridges = [mock_bridge]
        mock_game_session.current_budget = 1200  # After refund

        with qtbot.waitSignal(viewmodel.budget_changed, timeout=1000) as blocker:
            viewmodel.remove_bridge(1)

        assert blocker.args[0] == 1200

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_remove_bridge_emits_nodes_changed_signal(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp,
            qtbot
    ):
        """Test that remove_bridge emits nodes_changed signal on success."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        mock_game_session = viewmodel._game_session

        mock_bridge = Mock()
        mock_bridge.bridge_id = 1
        mock_game_session.network.bridges = [mock_bridge]

        with qtbot.waitSignal(viewmodel.nodes_changed, timeout=1000):
            viewmodel.remove_bridge(1)

    @patch('viewmodels.game_viewmodel.GameSession')
    def test_remove_bridge_emits_error_on_exception(
            self,
            mock_game_session_class,
            mock_db_service,
            qapp,
            qtbot
    ):
        """Test that remove_bridge emits error_occurred when exception occurs."""
        player_id = 1
        level_id = 1

        viewmodel = GameViewModel(player_id, level_id, mock_db_service)
        mock_game_session = viewmodel._game_session

        mock_bridge = Mock()
        mock_bridge.bridge_id = 1
        mock_game_session.network.bridges = [mock_bridge]
        mock_game_session.remove_bridge.side_effect = ValueError("Bridge cannot be removed")

        with qtbot.waitSignal(viewmodel.error_occurred, timeout=1000) as blocker:
            viewmodel.remove_bridge(1)

        assert "Failed to remove bridge" in blocker.args[0]
        assert "Bridge cannot be removed" in blocker.args[0]
