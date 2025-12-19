from models.bridge_type import BridgeType
from models.node import Node


class Bridge:
    """Represents a network connection (Bridge) in the game."""

    def __init__(self, bridge_id: int, from_node: Node, to_node: Node, bridge_type: BridgeType):
        """Initialize a bridge between two nodes.

        Args:
            bridge_id: Unique identifier of the bridge.
            from_node: Start node of the connection.
            to_node: End node of the connection.
            bridge_type: Type of this bridge, defines bandwidth and cost.
        """
        self.bridge_id = bridge_id
        self.from_node = from_node
        self.to_node = to_node
        self.bridge_type = bridge_type
