from viewmodels.view_items import NodeViewItem, BridgeViewItem


def test_node_view_item_equality():
    """Test NodeViewItem __eq__ comparison."""
    node1 = NodeViewItem(1, 100, 200, 3, 1, "SERVER")
    node2 = NodeViewItem(1, 100, 200, 3, 1, "SERVER")
    node3 = NodeViewItem(2, 100, 200, 3, 1, "SERVER")

    assert node1 == node2
    assert node1 != node3


def test_node_view_item_repr():
    """Test NodeViewItem string representation."""
    node = NodeViewItem(1, 100, 200, 3, 1, "SERVER")
    assert "node_id=1" in repr(node)
    assert "SERVER" in repr(node)


def test_bridge_view_item_structure():
    """Test BridgeViewItem data access."""
    grid_points = [(10, 20), (30, 40)]
    bridge = BridgeViewItem(1, 1, 2, "ETHERNET", grid_points)

    assert bridge.bridge_id == 1
    assert bridge.from_node_id == 1
    assert bridge.grid_points[0] == (10, 20)
    assert bridge.bridge_type == "ETHERNET"
