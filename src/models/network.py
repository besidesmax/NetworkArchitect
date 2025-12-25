from models.bridge import Bridge
from models.bridge_type import BridgeType
from models.grid_point import GridPoint
from models.node import Node
from models.validator import Validator


class Network:
    """Represents the network of a level containing all nodes and bridges."""

    def __init__(self):
        """Initialize an empty network for a level."""

        self.nodes: list[Node] = []
        self.bridges: list[Bridge] = []
        self.is_solved = False
        self.performance_score = 0.0
        self.redundancy_score = 0.0

    def add_node(self, node: Node) -> bool:
        """Add a node to the network if it is not already present.

        Args:
            node (Node): Node object to add to the network.

        Returns:
            bool: True if the node was added, False if it was already in the network.
        """
        # checks if node is already in the Network, and adds if not
        if node in self.nodes:
            return False
        self.nodes.append(node)
        return True

    def add_bridge(self, from_node: Node, grid_points: list[GridPoint], to_node: Node,
                   bridge_type: BridgeType) -> Bridge:
        """Place a bridge between two nodes after validating the path.

        Args:
            from_node (Node): Start node of the bridge.
            grid_points (list[GridPoint]): GridPoints along the bridge path.
            to_node (Node): End node of the bridge.
            bridge_type (BridgeType): Type of the bridge.

        Raises:
            ValueError: If grid_points is empty or any validation rule is violated.

        Returns:
            Bridge: The created bridge instance.
        """
        # tests grid_points isn't empty
        if len(grid_points) == 0:
            raise ValueError("Grid points list cannot be empty")

        # check that from_node and to_node are Node instances
        if not isinstance(from_node, Node):
            raise ValueError("from_node isn't Class Node")
        if not isinstance(to_node, Node):
            raise ValueError("to_node isn't Class Node")

        # tests if any GridPoint is already used
        Validator.is_grid_point_used(grid_points)
        # test if the 1. grid_point is next to from_node
        Validator.is_first_grid_point_adjacent(from_node, grid_points)
        # test if the last grid_point is next to from_node
        Validator.is_last_grid_point_adjacent(to_node, grid_points)
        # test if all grid_point are adjacent to each other
        Validator.are_grid_points_adjacent(grid_points)

        # add from_node to network
        self.add_node(from_node)
        # add to_node to network
        self.add_node(to_node)
        # raise current_connections of from_node by 1
        from_node.add_connection()
        # raise current_connections of to_node by 1
        to_node.add_connection()

        # create bridge
        bridge = Bridge(from_node, grid_points, to_node, bridge_type)
        # set all grid_point.used = True
        for i in range(len(grid_points)):
            grid_point1 = grid_points[i]
            grid_point1.used = True

        self.bridges.append(bridge)

        return bridge

    def reset_network(self) -> None:
        """Reset network state to an empty level network."""
        self.nodes: list[Node] = []
        self.bridges: list[Bridge] = []
        self.is_solved = False
        self.performance_score = 0.0
        self.redundancy_score = 0.0

    def remove_bridge(self, bridge_id: int) -> bool:
        """Remove a bridge with the given ID from the network.

        :param bridge_id: Unique identifier of the bridge to remove.
        :return: True if the bridge was successfully removed.
        :raises ValueError: If no bridge with the given ID exists in the network.
        """

        # Collect all existing bridge IDs in the network to validate the input.
        list_bridges_id = []
        for bridge in self.bridges:
            list_bridges_id.append(bridge.bridge_id)

        # If the requested ID is not known, fail fast with a clear error.
        if bridge_id not in list_bridges_id:
            raise ValueError(f"Bridge ID is not in the network")

        # Iterate over all bridges and remove the one with the matching ID
        # Also reset the 'used' flag on all grid points occupied by this bridge.
        for bridge in self.bridges:
            if bridge.bridge_id == bridge_id:
                self.bridges.remove(bridge)
                for grid_point in bridge.grid_points:
                    grid_point.used = False

        return True
