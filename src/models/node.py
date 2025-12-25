from models.node_type import NodeType
from models.grid_point import GridPoint


class Node:
    """Represents a network device (node) in the game."""
    all_instances: list['Node'] = []
    id_counter = 0

    def __init__(self, grid_point: list[GridPoint], node_type: NodeType) -> None:
        """Create network Node at grid position with type-specific connection limits.

        Args:
            grid_point: List with exactly one GridPoint (X,Y position).
            node_type: Defines max connections (SERVER=8, FIREWALL=2).

        Raises:
            ValueError: If grid_point does not contain exactly one GridPoint or the GridPoint is already used.
        """
        # Global unique ID for all nodes in session
        self.node_id = Node.id_counter
        Node.id_counter += 1
        # Node requires exactly 1 GridPoint position
        if len(grid_point) != 1:
            raise ValueError("Node requires exactly 1 GridPoint")
        # checks if grid_point is already used
        if grid_point[0].used is True:
            raise ValueError(f" GridPoint {grid_point[0].grid_point_id} is already used")
        grid_point[0].used = True
        self.grid_point = grid_point
        # determines properties
        self.node_type = node_type
        self.current_connections = 0

    def add_connection(self) -> bool:
        """Add one connection to this node respecting capacity limits.

         Returns:
             bool: True if the connection was successfully added.

         Raises:
             ValueError: If the maximum number of connections for this node is already reached.
        """
        # Ensure that the node does not exceed its allowed connection capacity.
        if self.current_connections >= self.node_type.max_connections:
            raise ValueError(f"Maximum number of connections already reached")
        # Increment the number of active connections for this node.
        self.current_connections += 1
        return True

    def remove_connection(self) -> bool:
        """Decrease the number of active connections for this node by one.

         Returns:
             bool: True if the connection was successfully removed.

         Raises:
             ValueError:  If there are no active connections to remove.
        """
        # Prevent the connection count from dropping below zero.
        if self.current_connections == 0:
            raise ValueError(f"CurrentConnections is already 0")

        # Decrement the number of active connections for this node.
        self.current_connections -= 1
        return True

    @staticmethod
    def reset_all_nodes() -> None:
        """Reset connection counters for all registered nodes."""
        for node in Node.all_instances:
            node.current_connections = 0
