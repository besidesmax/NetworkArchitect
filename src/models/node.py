from models.node_type import NodeType
from models.grid_point import GridPoint

class Node:
    """Represents a network device (node) in the game."""

    def __init__(self, node_id: int, grid_point: GridPoint, node_type: NodeType):
        """Initialize a node with position = GridPoint, type and connection capacity.

        Args:
            node_id: Unique identifier of the node on the board.
            grid_point: X and Y coordinate of the node on the board grid.
            node_type: Type of node, defines its maximum connections.
        """
        self.node_id = node_id
        self.grid_point = grid_point
        self.node_type = node_type
        self.current_connections = 0

    def add_connection(self) -> bool:
        """Add one bridge connection to this node (GR-06).

        Returns:
            True if the connection was added successfully,
            False if the node has already reached its maximum capacity.
        """
        if self.current_connections >= self.node_type.max_connections:
            return False
        self.current_connections += 1
        return True
