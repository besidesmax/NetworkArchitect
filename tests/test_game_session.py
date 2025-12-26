from models.bridge_type import BridgeType
from models.difficulty import Difficulty
from models.game_session import GameSession
from models.level import Level
from models.node import Node
from models.node_type import NodeType
from models.player import Player


def test_place_bridge():
    """GR-03: Tests bridge placement success, budget deduction, low budget failure.

    Verifies:
    - Bridge added to network.bridges
    - Budget deducted by BridgeType.ETHERNET.cost (10)
    - Low budget (5 < 10) → False, state unchanged
    """
    player1 = Player("TestPlayer")
    level1 = Level(Difficulty.LIGHT, 1000, 5000)
    session = GameSession(player1, level1)

    # add Nodes
    node1 = Node([session.level.game_board[2]], NodeType.CLIENT)
    node2 = Node([session.level.game_board[41]], NodeType.CLIENT)
    node3 = Node([session.level.game_board[21]], NodeType.SERVER)
    node4 = Node([session.level.game_board[23]], NodeType.CLIENT)
    node5 = Node([session.level.game_board[25]], NodeType.CLIENT)
    node6 = Node([session.level.game_board[0]], NodeType.CLIENT)

    # add node_config
    session.level.node_config.nodes = [node1, node2, node3, node4, node5, node6]
    start_budget = session.level.start_budget
    start_bridge = list(session.network.bridges)

    session.place_bridge(node4, [session.level.game_board[24]], node5, BridgeType.ETHERNET)
    bridge = session.network.bridges[0]

    # Valid bridge is added to network."""
    assert bridge not in start_bridge and bridge in session.network.bridges

    # GR-03: Valid bridge placement deducts budget."""
    assert start_budget == session.current_budget + BridgeType.ETHERNET.cost

    # Valid if low budget hiders placement
    session.current_budget = 5
    assert not session.place_bridge(node4, [session.level.game_board[32]], node2, BridgeType.ETHERNET)


def test_remove_bridge():
    """GR-04+GR-15: Tests bridge removal refunds budget.

    Verifies:
    - Existing bridge → remove_bridge() == True
    - budget += bridge.bridge_type.cost (refund)
    - bridge no longer in network.bridges
    """
    # Setup: LIGHT level with minimal nodes
    player1 = Player("TestPlayer")
    level1 = Level(Difficulty.LIGHT, 1000, 5000)
    session = GameSession(player1, level1)

    # GR-08: Configure minimal level nodes
    node4 = Node([session.level.game_board[23]], NodeType.CLIENT)
    node5 = Node([session.level.game_board[25]], NodeType.CLIENT)

    # GR-03: Place bridge first (budget -= 10)
    session.place_bridge(node4, [session.level.game_board[24]], node5, BridgeType.ETHERNET)
    bridge = session.network.bridges[0]
    start_budget = session.current_budget

    # GR-04+GR-15: Remove → refund budget + bridge deleted
    assert session.remove_bridge(bridge)
    assert session.current_budget == bridge.bridge_type.cost + start_budget
    assert bridge not in session.network.bridges


def test_is_it_solved_complete():
    """GR-05+GR-09: Verify complete server-reachable network.

    Tests:
    - GR-08: All 6 level nodes present in network
    - GR-09: Server has ≥2 connections
    - GR-05: BFS reaches all nodes: Server↔C1↔C6, Server↔C2, Server↔C3↔C4
    """
    player1 = Player("TestPlayer")
    level1 = Level(Difficulty.LIGHT, 1000, 5000)
    session = GameSession(player1, level1)

    # add Nodes
    node1 = Node([session.level.game_board[2]], NodeType.CLIENT)
    node2 = Node([session.level.game_board[41]], NodeType.CLIENT)
    node3 = Node([session.level.game_board[21]], NodeType.SERVER)
    node4 = Node([session.level.game_board[23]], NodeType.CLIENT)
    node5 = Node([session.level.game_board[25]], NodeType.CLIENT)
    node6 = Node([session.level.game_board[0]], NodeType.CLIENT)

    # add node_config
    session.level.node_config.nodes = [node1, node2, node3, node4, node5, node6]

    # add bridges
    session.place_bridge(node1, [session.level.game_board[3], session.level.game_board[12]], node3,
                         BridgeType.FIBER)
    session.place_bridge(node3, [session.level.game_board[30],
                                 session.level.game_board[31],
                                 session.level.game_board[32]], node2, BridgeType.WIFI_24G)
    session.place_bridge(node3, [session.level.game_board[20],
                                 session.level.game_board[29],
                                 session.level.game_board[38],
                                 session.level.game_board[39],
                                 session.level.game_board[40]], node2, BridgeType.ETHERNET)
    session.place_bridge(node4, [session.level.game_board[24]], node5, BridgeType.ETHERNET)
    session.place_bridge(node6, [session.level.game_board[1]], node1, BridgeType.ETHERNET)
    session.place_bridge(node3, [session.level.game_board[22]], node4, BridgeType.ETHERNET)

    assert session.is_it_solved()
