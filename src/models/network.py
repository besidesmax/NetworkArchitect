from models.node import Node
from models.grid_point import GridPoint
from models.bridge_type import BridgeType
from models.bridge import Bridge
from models.validator import Validator


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
        """
        # checks if node is already in the Network
        if node in self.nodes:
            raise ValueError(f" Node {node.node_id} is already used in Network")
        self.nodes.append(node)
        return True

    def place_bridge(self, from_node: Node, grid_points: list[GridPoint], to_node: Node,
                     bridge_type: BridgeType) -> Bridge:
        # tests grid_points isn't empty
        if len(grid_points) == 0:
            raise ValueError("Grid points list cannot be empty")

        # tests if GridPoint is already used
        Validator.is_grid_point_used(grid_points)
        # test if the 1. grid_point is next to from_node
        Validator.is_first_grid_point_adjacent(from_node, grid_points)
        # test if the last grid_point is next to from_node
        Validator.is_last_grid_point_adjacent(to_node, grid_points)
        # test if all grid_point are adjacent to each other
        Validator.are_grid_points_adjacent(grid_points)
        # raise current_connections of from_node by 1
        from_node.add_connection()
        # raise current_connections of to_node by 1
        to_node.add_connection()
        # create bridge
        bridge = Bridge(from_node, grid_points, to_node, bridge_type)
        # set all grid_point.used = True
        for i in range(len(grid_points) - 1):
            grid_point1 = grid_points[i]
            grid_point1.used = True

        self.bridges.append(bridge)
        return bridge
