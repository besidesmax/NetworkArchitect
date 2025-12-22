from models.bridge_type import BridgeType
from models.node import Node
from models.grid_point import GridPoint


class Bridge:
    """Represents a network connection (bridge) between two nodes."""

    id_counter = 1

    def __init__(self, from_node: Node, grid_points: list[GridPoint], to_node: Node,
                 bridge_type: BridgeType) -> None:
        """Initialize a bridge between two nodes.

        Args:
            from_node (Node): Start node of the connection.
            grid_points (list[GridPoint]): GridPoints along the bridge path.
            to_node (Node): End node of the connection.
            bridge_type (BridgeType): Type of this bridge defining bandwidth and cost.
        """
        # Assign unique bridge ID
        self.bridge_id = Bridge.id_counter
        Bridge.id_counter += 1

        # Store bridge attributes
        self.grid_points: list[GridPoint] = grid_points
        self.from_node = from_node
        self.to_node = to_node
        self.bridge_type = bridge_type
