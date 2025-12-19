from models.bridge_type import BridgeType
from models.node import Node


class Bridge:
    """Represents a network connection (Bridge) in the game."""

    def __init__(self, bridge_id: int, from_node: Node, to_node: Node, bridge_type: BridgeType):
        self.bridge_id = bridge_id
        self.from_node = Node
        self.to_node = Node
        self.bridge_type = BridgeType

    def get_bandwidth(self) -> int:
        """shows the bandwith of the connection"""
        return self.bridge_type.bandwidth





