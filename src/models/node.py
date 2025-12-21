from models.node_type import NodeType
from models.grid_point import GridPoint
from models.validator import Validator


class Node:
    """Represents a network device (node) in the game."""

    id_counter = 1

    def __init__(self, grid_point: list[GridPoint], node_type: NodeType):
        """Initialize a node with position = GridPoint, type and connection capacity.

        Args:
            grid_point: X and Y coordinate of the node on the board grid.
            node_type: Type of node, defines its maximum connections.
        """
        # define ID
        self.node_id = Node.id_counter
        Node.id_counter += 1
        # test if GridPoint is already used
        Validator.is_grid_point_used(grid_point)
        self.grid_point = grid_point
        # defines rest of the attributes
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
