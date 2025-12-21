from models.node import Node
from models.grid_point import GridPoint
from models.bridge_type import BridgeType
from models.bridge import Bridge


class Network:
    """ represents the Network of a Level, with includes alls Nodes and Bridges"""

    def __init__(self):
        """Represents the network of a level. Starts empty - nodes and bridges added dynamically during gameplay."""

        self.nodes: list[Node] = []
        self.bridges: list[Bridge] = []
        self.is_solved = False
        self.performance_score = 0.0
        self.redundancy_score = 0.0

    def add_node(self, node: Node) -> bool:
        """Adds a single node to the network.

        Args:
            node (Node): The node object to add to the network
        Returns:
            bool: True if node was successfully added,
            False if node already exists
        """
        if node in self.nodes:
            return False
        self.nodes.append(node)

        return True

    def place_bridge(self, from_node: Node, grid_points: list[GridPoint], to_node: Node,
                     bridge_type: BridgeType) -> Bridge:

        from_node.add_connection()
        to_node.add_connection()
        bridge = Bridge(from_node, grid_points, to_node, bridge_type)
        self.bridges.append(bridge)
        return bridge

