import pytest

from models.bridge_type import BridgeType
from models.grid_point import create_board
from models.network import Network
from models.node import Node
from models.node_type import NodeType


def test_add_node() -> None:
    network1 = Network()
    board = create_board(3, 3)
    node1 = Node([board[0]], NodeType.CLIENT)

    # Ensure add_node adds the node to the network
    assert len(network1.nodes) == 0
    network1.add_node(node1)
    assert node1 in network1.nodes


def test_place_bridge() -> None:
    network1 = Network()
    board = create_board(3, 3)
    node1 = Node([board[0]], NodeType.CLIENT)
    node2 = Node([board[5]], NodeType.CLIENT)

    # Ensure place_bridge adds a bridge to the network
    assert len(network1.bridges) == 0
    bridge1 = network1.place_bridge(node1, [board[3], board[4]], node2, BridgeType.FIBER)
    assert bridge1 in network1.bridges

    # Using an empty GridPoint list must raise ValueError
    with pytest.raises(ValueError):
        network1.place_bridge(node1, [], node2, BridgeType.FIBER)

    network1.reset_network()
    board = create_board(3, 3)
    node1 = Node([board[0]], NodeType.CLIENT)
    node2 = Node([board[5]], NodeType.CLIENT)
    node3 = Node([board[7]], NodeType.CLIENT)

    # Reusing an already used GridPoint must raise ValueError
    network1.place_bridge(node1, [board[3], board[4]], node2, BridgeType.FIBER)
    with pytest.raises(ValueError):
        network1.place_bridge(node2, [board[4]], node3, BridgeType.FIBER)

    # First GridPoint not adjacent to from_node must raise ValueError
    network1.reset_network()
    board = create_board(3, 3)
    node2 = Node([board[5]], NodeType.CLIENT)
    node3 = Node([board[7]], NodeType.CLIENT)
    with pytest.raises(ValueError):
        network1.place_bridge(node2, [board[3]], node3, BridgeType.FIBER)

    # Last GridPoint not adjacent to to_node must raise ValueError
    network1.reset_network()
    board = create_board(3, 3)
    node2 = Node([board[5]], NodeType.CLIENT)
    node3 = Node([board[7]], NodeType.CLIENT)
    with pytest.raises(ValueError):
        network1.place_bridge(node2, [board[3]], node3, BridgeType.FIBER)

    # Non-adjacent GridPoints in the path must raise ValueError
    network1.reset_network()
    board = create_board(3, 3)
    node2 = Node([board[5]], NodeType.CLIENT)
    node3 = Node([board[7]], NodeType.CLIENT)
    with pytest.raises(ValueError):
        network1.place_bridge(node2, [board[2], board[1], board[0], board[6]], node3, BridgeType.FIBER)

    # Adding a bridge must increase current_connections on both nodes
    network1.reset_network()
    board = create_board(3, 3)
    node2 = Node([board[5]], NodeType.CLIENT)
    node3 = Node([board[7]], NodeType.CLIENT)

    node2_0 = node2.current_connections
    node3_0 = node3.current_connections

    assert node2_0 == 0
    assert node3_0 == 0

    network1.place_bridge(node2, [board[4]], node3, BridgeType.FIBER)
    node2_1 = node2.current_connections
    node3_1 = node3.current_connections
    assert node2_1 == 1
    assert node3_1 == 1
