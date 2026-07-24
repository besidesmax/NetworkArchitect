from network_architect.models.game_session import GameSession
from network_architect.models.level import Level
from network_architect.models.player import Player
from network_architect.models.difficulty import Difficulty
from network_architect.models.node import Node
from network_architect.models.node_type import NodeType
from network_architect.models.bridge_type import BridgeType

player = Player("test")
level = Level(Difficulty.LIGHT, 1000, 1000, 1000)
original_session = GameSession(player, level)

node1 = Node([level.game_board[2]], NodeType.SERVER)
node2 = Node([level.game_board[5]], NodeType.CLIENT)
node3 = Node([level.game_board[9]], NodeType.CLIENT)
node4 = Node([level.game_board[12]], NodeType.ROUTER)
node5 = Node([level.game_board[17]], NodeType.CLIENT)
node6 = Node([level.game_board[31]], NodeType.CLIENT)
node7 = Node([level.game_board[38]], NodeType.CLIENT)

level.node_config.add_node(node1)
level.node_config.add_node(node2)
level.node_config.add_node(node3)
level.node_config.add_node(node4)
level.node_config.add_node(node5)
level.node_config.add_node(node6)
level.node_config.add_node(node7)

original_session.place_bridge(node1, [level.game_board[1], level.game_board[0]], node3, BridgeType.FIBER)
original_session.place_bridge(node1, [level.game_board[3], level.game_board[4]], node2, BridgeType.FIBER)
original_session.place_bridge(node2, [level.game_board[6], level.game_board[7], level.game_board[8]], node5,
                              BridgeType.FIBER)
original_session.place_bridge(node3, [level.game_board[10], level.game_board[11]], node4, BridgeType.FIBER)
original_session.place_bridge(node4, [level.game_board[13], level.game_board[22]], node6, BridgeType.FIBER)
original_session.place_bridge(node6, [level.game_board[30], level.game_board[29]], node7, BridgeType.FIBER)

print(original_session.is_it_solved())
print(original_session.calculate_redundancy_score())
