from NodeType import NodeType


class Node:
    """Represents a network device (node) in the game."""

    def __init__(self, node_id: int, x: int, y: int, node_type: NodeType):
        """
                Initialize a node with position, type and connection capacity.

        Args:
            node_id: Unique identifier of the node on the board.
            x: X coordinate of the node on the board grid.
            y: Y coordinate of the node on the board grid.
            node_type: Type of node, defines its maximum connections.
        """
        self.node_id = node_id
        self.position_x = x
        self.position_y = y
        self.node_type = node_type
        self.current_connections = 0
        self.max_connections = node_type.max_connections

    def add_connection(self) -> bool:
        """Add one bridge connection to this node (GR-06).

        Returns:
            True if the connection was added successfully,
            False if the node has already reached its maximum capacity.
        """
        if self.current_connections >= self.max_connections:
            return False
        self.current_connections += 1
        return True
