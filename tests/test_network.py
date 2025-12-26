import pytest
from models.bridge_type import BridgeType
from models.grid_point import GridPoint
from models.network import Network
from models.node import Node
from models.node_type import NodeType
from models.bridge import Bridge


def create_board(x: int, y: int) -> list:
    height = x
    width = y

    board: list[GridPoint] = []
    for x in range(width):
        for y in range(height):
            board.append(GridPoint(x, y))

    return board


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
    bridge1 = network1.add_bridge(node1, [board[3], board[4]], node2, BridgeType.FIBER)
    assert bridge1 in network1.bridges

    # Using an empty GridPoint list must raise ValueError
    with pytest.raises(ValueError):
        network1.add_bridge(node1, [], node2, BridgeType.FIBER)

    network1.reset_network()
    board = create_board(3, 3)
    node1 = Node([board[0]], NodeType.CLIENT)
    node2 = Node([board[5]], NodeType.CLIENT)
    node3 = Node([board[7]], NodeType.CLIENT)

    # Reusing an already used GridPoint must raise ValueError
    network1.add_bridge(node1, [board[3], board[4]], node2, BridgeType.FIBER)
    with pytest.raises(ValueError):
        network1.add_bridge(node2, [board[4]], node3, BridgeType.FIBER)

    # First GridPoint not adjacent to from_node must raise ValueError
    network1.reset_network()
    board = create_board(3, 3)
    node2 = Node([board[5]], NodeType.CLIENT)
    node3 = Node([board[7]], NodeType.CLIENT)
    with pytest.raises(ValueError):
        network1.add_bridge(node2, [board[3]], node3, BridgeType.FIBER)

    # Last GridPoint not adjacent to to_node must raise ValueError
    network1.reset_network()
    board = create_board(3, 3)
    node2 = Node([board[5]], NodeType.CLIENT)
    node3 = Node([board[7]], NodeType.CLIENT)
    with pytest.raises(ValueError):
        network1.add_bridge(node2, [board[3]], node3, BridgeType.FIBER)

    # Non-adjacent GridPoints in the path must raise ValueError
    network1.reset_network()
    board = create_board(3, 3)
    node2 = Node([board[5]], NodeType.CLIENT)
    node3 = Node([board[7]], NodeType.CLIENT)
    with pytest.raises(ValueError):
        network1.add_bridge(node2, [board[2], board[1], board[0], board[6]], node3, BridgeType.FIBER)

    # Adding a bridge must increase current_connections on both nodes
    network1.reset_network()
    board = create_board(3, 3)
    node2 = Node([board[5]], NodeType.CLIENT)
    node3 = Node([board[7]], NodeType.CLIENT)

    node2_0 = node2.current_connections
    node3_0 = node3.current_connections

    assert node2_0 == 0
    assert node3_0 == 0

    network1.add_bridge(node2, [board[4]], node3, BridgeType.FIBER)
    node2_1 = node2.current_connections
    node3_1 = node3.current_connections
    assert node2_1 == 1
    assert node3_1 == 1


def test_delete_bridge() -> None:
    network1 = Network()
    board = create_board(3, 3)
    node1 = Node([board[0]], NodeType.CLIENT)
    node2 = Node([board[5]], NodeType.CLIENT)
    bridge1 = network1.add_bridge(node1, [board[3], board[4]], node2, BridgeType.FIBER)
    bridge2 = Bridge(node1, [board[3], board[4]], node2, BridgeType.FIBER)

    # deleting a bridge that isn't in the network have to raise a ValueError
    with pytest.raises(ValueError):
        network1.delete_bridge(bridge2)

    # check if deleting a bridge, removes it form the network
    start_bridges = list(network1.bridges)
    network1.delete_bridge(bridge1)
    assert start_bridges != network1.bridges

    # check if deleting a bridge, change all bridges.grid_point.used to false
    bridge1 = network1.add_bridge(node1, [board[3], board[4]], node2, BridgeType.FIBER)
    start_used = {}
    for grid_point in bridge1.grid_points:
        start_used[grid_point] = grid_point.used
    network1.delete_bridge(bridge1)
    finished_used = {}
    for grid_point in bridge1.grid_points:
        finished_used[grid_point] = grid_point.used

    assert start_used != finished_used

    # check if current_connection of from_node and to_node is decreased by 1
    bridge1 = network1.add_bridge(node1, [board[3], board[4]], node2, BridgeType.FIBER)
    from_node_connection = bridge1.from_node.current_connections
    to_node_connection = bridge1.to_node.current_connections
    network1.delete_bridge(bridge1)
    assert from_node_connection == (bridge1.from_node.current_connections + 1)
    assert to_node_connection == (bridge1.to_node.current_connections + 1)

    # Verify that nodes are removed once their current_connections reach zero
    bridge1 = network1.add_bridge(node1, [board[3], board[4]], node2, BridgeType.FIBER)
    from_node = bridge1.from_node
    to_node = bridge1.to_node
    start_nodes = list(network1.nodes)
    network1.delete_bridge(bridge1)
    assert from_node in start_nodes
    assert to_node in start_nodes
    assert from_node not in network1.nodes
    assert to_node not in network1.nodes
