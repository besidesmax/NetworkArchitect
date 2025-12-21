from models.bridge_type import BridgeType
from models.node import Node
from models.grid_point import GridPoint
from models.validator import Validator


class Bridge:
    """Represents a network connection (Bridge) in the game."""

    id_counter = 1

    def __init__(self, from_node: Node, grid_points: list[GridPoint], to_node: Node,
                 bridge_type: BridgeType):
        """Initialize a bridge between two nodes.

        Args:
            from_node: Start node of the connection.
            grid_points: List of GridPoints located along the bridge's path.
            to_node: End node of the connection.
            bridge_type: Type of this bridge, defines bandwidth and cost.
        """
        # sets the bridge_id
        self.bridge_id = Bridge.id_counter
        Bridge.id_counter += 1
        # defines rest of the attributes
        self.grid_points: list[GridPoint] = grid_points
        self.from_node = from_node
        self.to_node = to_node
        self.bridge_type = bridge_type
