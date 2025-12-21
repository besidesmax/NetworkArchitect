from models.bridge_type import BridgeType
from models.node import Node
from models.grid_point import GridPoint


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

        # test if GridPoint is already used
        for grid_point in grid_points:
            if grid_point.used:
                raise ValueError("GridPoint", grid_point.grid_point_id, "is already used")
            grid_point.used = True
        self.from_node = from_node
        self.grid_points = grid_points
        self.to_node = to_node
        self.bridge_type = bridge_type
