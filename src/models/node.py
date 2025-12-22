from models.node_type import NodeType
from models.grid_point import GridPoint


class Node:
    """Represents a network device (node) in the game."""

    id_counter = 1

    def __init__(self, grid_point: list[GridPoint], node_type: NodeType):
        """Create network Node at grid position with type-specific connection limits.

        Args:
            grid_point: List with exactly one GridPoint (X,Y position).
            node_type: Defines max connections (SERVER=8, FIREWALL=2).

        Raises:
            ValueError: If grid_point does not contain exactly 1 GridPoint.
        """
        # Global unique ID for all nodes in session
        self.node_id = Node.id_counter
        Node.id_counter += 1
        # Node requires exactly 1 GridPoint position
        if len(grid_point) != 1:
            raise ValueError("Node requires exactly 1 GridPoint")
        self.grid_point = grid_point
        # determines properties
        self.node_type = node_type
        self.current_connections = 0

    def add_connection(self) -> bool:
        """Add one connection to this node (GR-06).

        Returns:
            True if capacity allows and connection was added successfully,
            False if the node has already reached its maximum capacity. (GR-06/10)
        """
        if self.current_connections >= self.node_type.max_connections:
            return False
        self.current_connections += 1
        return True
