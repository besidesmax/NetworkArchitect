import pytest
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF
from views.game_view import GameView


@pytest.fixture
def app():
    """Create QApplication instance for Qt widgets."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def mock_viewmodel():
    """Create mock ViewModel with test data."""
    viewmodel = Mock()

    # Mock properties
    viewmodel.game_board = [
        {"id": 0, "x": 0, "y": 0},
        {"id": 1, "x": 1, "y": 0},
        {"id": 2, "x": 2, "y": 0},
    ]

    viewmodel.nodes = [
        {"id": 0, "x": 0, "y": 0, "type": "SERVER", "max_connections": 4, "current_connections": 0},
        {"id": 1, "x": 2, "y": 0, "type": "CLIENT", "max_connections": 2, "current_connections": 0},
    ]

    viewmodel.bridges = []

    viewmodel.current_budget = 1000
    viewmodel.selected_bridge_type = ""

    viewmodel.available_bridge_types = [
        {"name": "ETHERNET", "bandwidth": 100, "cost": 50},
        {"name": "FIBER", "bandwidth": 1000, "cost": 200},
    ]

    # Mock signals
    viewmodel.time_updated = Mock()
    viewmodel.time_updated.connect = Mock()
    viewmodel.budget_changed = Mock()
    viewmodel.budget_changed.connect = Mock()
    viewmodel.confirm_navigation = Mock()
    viewmodel.confirm_navigation.connect = Mock()
    viewmodel.error_occurred = Mock()
    viewmodel.error_occurred.connect = Mock()
    viewmodel.level_completed = Mock()
    viewmodel.level_completed.connect = Mock()
    viewmodel.game_reset = Mock()
    viewmodel.game_reset.connect = Mock()
    viewmodel.nodes_changed = Mock()
    viewmodel.nodes_changed.connect = Mock()
    viewmodel.bridges_changed = Mock()
    viewmodel.bridges_changed.connect = Mock()

    return viewmodel


@pytest.fixture
def game_view(app, mock_viewmodel):
    """Create GameView with mocked ViewModel."""
    view = GameView(mock_viewmodel)
    return view


def test_bridge_place_button_exists(game_view):
    """Test that bridge place button exists and is checkable."""
    assert game_view.bridge_place_btn is not None
    assert game_view.bridge_place_btn.isCheckable()


def test_bridge_delete_button_exists(game_view):
    """Test that bridge delete button exists and is checkable."""
    assert game_view.bridge_delete_btn is not None
    assert game_view.bridge_delete_btn.isCheckable()


def test_bridge_placement_flow(game_view, mock_viewmodel):
    """Test basic bridge placement flow."""
    # Select bridge type
    mock_viewmodel.selected_bridge_type = "ETHERNET"

    # Simulate bridge placement
    mock_bridge = {
        "bridge_id": 0,
        "from_node_id": 0,
        "from_node_x": 0,
        "from_node_y": 0,
        "to_node_id": 1,
        "to_node_x": 2,
        "to_node_y": 0,
        "grid_points": [],
        "bridge_type": "ETHERNET"
    }
    mock_viewmodel.bridges = [mock_bridge]

    # Call place_bridge_vm
    game_view.viewmodel.place_bridge_vm(
        from_node_id=0,
        grid_points_id=[],
        to_node_id=1
    )

    # Verify method was called
    game_view.viewmodel.place_bridge_vm.assert_called_once_with(
        from_node_id=0,
        grid_points_id=[],
        to_node_id=1
    )


def test_bridge_deletion_flow(game_view, mock_viewmodel):
    """Test basic bridge deletion flow."""
    # Setup: Bridge exists
    mock_bridge = {
        "bridge_id": 0,
        "from_node_id": 0,
        "from_node_x": 0,
        "from_node_y": 0,
        "to_node_id": 1,
        "to_node_x": 2,
        "to_node_y": 0,
        "grid_points": [],
        "bridge_type": "ETHERNET"
    }
    mock_viewmodel.bridges = [mock_bridge]

    # Delete bridge
    game_view.viewmodel.remove_bridge(bridge_id=0)

    # Verify method was called
    game_view.viewmodel.remove_bridge.assert_called_once_with(bridge_id=0)


def test_mode_switching(game_view):
    """Test switching between place and delete modes."""
    # Initially unchecked
    assert not game_view.bridge_place_btn.isChecked()
    assert not game_view.bridge_delete_btn.isChecked()

    # Check delete mode
    game_view.bridge_delete_btn.setChecked(True)
    assert game_view.bridge_delete_btn.isChecked()

    # Uncheck
    game_view.bridge_delete_btn.setChecked(False)
    assert not game_view.bridge_delete_btn.isChecked()


def test_selection_reset(game_view):
    """Test that reset_selected_items clears all selections."""
    # Setup: Simulate selections (set to None initially)
    game_view._selected_from_node_item = None
    game_view._selected_to_node_item = None
    game_view._selected_grid_points_item = []

    # Call reset
    game_view.reset_selected_items(None, [], None)

    # Verify all cleared
    assert game_view._selected_from_node_item is None
    assert game_view._selected_to_node_item is None
    assert game_view._selected_grid_points_item == []


def test_right_click_resets_selection(game_view):
    """Test that right-click triggers selection reset."""
    # Setup selections
    game_view._selected_from_node_item = None
    game_view._selected_to_node_item = None
    game_view._selected_grid_points_item = []

    # Trigger right-click handler
    game_view._on_canvas_clicked_right()

    # Verify reset was called (selections should be None/empty)
    assert game_view._selected_from_node_item is None
    assert game_view._selected_to_node_item is None
    assert game_view._selected_grid_points_item == []
