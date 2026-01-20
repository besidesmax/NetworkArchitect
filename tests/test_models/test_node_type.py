from models.node_type import NodeType


def test_node_type_properties():
    """Verify NodeType min and max connection constraints."""

    # test if max_connections and min_connection of NodeType are correct
    expected_max_connections = {
        NodeType.SERVER: 4,
        NodeType.CLIENT: 4,
        NodeType.FIREWALL: 2,
        NodeType.ROUTER: 4
    }

    expected_min_connections = {
        NodeType.SERVER: 2,
        NodeType.CLIENT: 0,
        NodeType.FIREWALL: 0,
        NodeType.ROUTER: 0
    }
    for node_type, expected in expected_max_connections.items():
        assert node_type.max_connections == expected

    for node_type, expected in expected_min_connections.items():
        assert node_type.min_connections == expected
