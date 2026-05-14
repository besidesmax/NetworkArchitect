import pytest

from models.bridge import Bridge
from models.bridge_type import BridgeType
from models.grid_point import GridPoint
from models.network import Network
from models.node import Node
from models.node_type import NodeType


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


def test_add_bridge() -> None:
    """
    Test placing a bridge between two nodes in the network.

    Verifies that:
    - A valid bridge is successfully added to the network.
    - Reusing an already occupied GridPoint raises a ValueError.
    - A non-adjacent first GridPoint raises a ValueError.
    - Non-adjacent GridPoints in the path raise a ValueError.
    - Adding a bridge increases current_connections on both nodes by 1.
    - Passing a non-Node object as from_node or to_node raises a ValueError.
    """
    # Arrange
    network1 = Network()
    board = create_board(3, 3)
    node1 = Node([board[0]], NodeType.CLIENT)
    node2 = Node([board[5]], NodeType.CLIENT)

    # Act & Assert 1: Valid bridge is added to the network
    assert len(network1.bridges) == 0
    bridge1 = network1.add_bridge(node1, [board[3], board[4]], node2, BridgeType.FIBER)
    assert bridge1 in network1.bridges

    # Arrange
    network1.reset_network()
    board = create_board(3, 3)
    node1 = Node([board[0]], NodeType.CLIENT)
    node2 = Node([board[5]], NodeType.CLIENT)
    node3 = Node([board[7]], NodeType.CLIENT)

    # Act & Assert 2: Reusing an already used GridPoint raises ValueError
    network1.add_bridge(node1, [board[3], board[4]], node2, BridgeType.FIBER)
    with pytest.raises(ValueError):
        network1.add_bridge(node2, [board[4]], node3, BridgeType.FIBER)

    # Arrange
    network1.reset_network()
    board = create_board(3, 3)
    node2 = Node([board[5]], NodeType.CLIENT)
    node3 = Node([board[7]], NodeType.CLIENT)

    # Act & Assert 3: First GridPoint not adjacent to from_node raises ValueError
    with pytest.raises(ValueError):
        network1.add_bridge(node2, [board[3]], node3, BridgeType.FIBER)

    # Arrange
    network1.reset_network()
    board = create_board(3, 3)
    node2 = Node([board[5]], NodeType.CLIENT)
    node3 = Node([board[7]], NodeType.CLIENT)

    # Act & Assert 4: Non-adjacent GridPoints in the path raise ValueError
    with pytest.raises(ValueError):
        network1.add_bridge(node2, [board[2], board[1], board[0], board[6]], node3, BridgeType.FIBER)

    # Arrange
    network1.reset_network()
    board = create_board(3, 3)
    node2 = Node([board[5]], NodeType.CLIENT)
    node3 = Node([board[7]], NodeType.CLIENT)

    node2_0 = node2.current_connections
    node3_0 = node3.current_connections

    assert node2_0 == 0
    assert node3_0 == 0

    # Act & Assert 5: Adding a bridge increases current_connections on both nodes by 1
    network1.add_bridge(node2, [board[4]], node3, BridgeType.FIBER)
    assert node2.current_connections == 1
    assert node3.current_connections == 1

    # Act & Assert 6: Passing a non-Node object as from_node or to_node raises ValueError
    with pytest.raises(ValueError):
        network1.add_bridge("not_a_node", [board[4]], node3, BridgeType.FIBER)
    with pytest.raises(ValueError):
        network1.add_bridge(node2, [board[4]], "not_a_node", BridgeType.FIBER)


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


def test_find_path() -> None:
    network1 = Network()
    # Create test board and server/client nodes at specific positions
    board1 = create_board(9, 5)
    node0 = Node([board1[21]], NodeType.SERVER)
    node1 = Node([board1[41]], NodeType.CLIENT)
    node2 = Node([board1[23]], NodeType.CLIENT)
    node3 = Node([board1[43]], NodeType.CLIENT)

    # add bridges
    network1.add_bridge(node1, [board1[40], board1[39], board1[30]], node0, BridgeType.FIBER)
    network1.add_bridge(node2, [board1[32]], node1, BridgeType.FIBER)
    network1.add_bridge(node0, [board1[22]], node2, BridgeType.ETHERNET)

    assert len(network1.find_path(node1)) == 2

    # add bridge
    network1.add_bridge(node1, [board1[42]], node3, BridgeType.ETHERNET)
    assert len(network1.find_path(node1)) == 2

    # add bridge
    network1.add_bridge(node3, [board1[34], board1[25], board1[24]], node2, BridgeType.ETHERNET)
    assert len(network1.find_path(node1)) == 5


def test_get_server() -> None:
    """
    Test retrieving the server node from the network.

    Verifies that:
    - Calling get_server() on a network without a server node raises a ValueError.
    - Calling get_server() returns the correct server node after it has been added.
    """
    # Arrange
    network1 = Network()
    gp_node = GridPoint(1, 1)
    node1 = Node([gp_node], NodeType.SERVER)

    # Act & Assert 1: No server in network raises ValueError
    with pytest.raises(ValueError):
        network1.get_server()

    # Act & Assert 2: Server node is returned after being added
    network1.add_node(node1)
    assert network1.get_server() == node1
