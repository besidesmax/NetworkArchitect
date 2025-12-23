from models.node import Node


class NodeConfig:
    """Stores all nodes of a single level."""

    id_counter = 1

    def __init__(self) -> None:
        self.node_config_id = NodeConfig.id_counter
        NodeConfig.id_counter += 1
        self.nodes: list[Node] = []

    def add_node(self, node: Node) -> bool:
        """Adds a node to this configuration.

        Args:
            node (Node): Node instance to add.

        Returns:
            bool: True if the node was added successfully.

        Raises:
            ValueError: If the node is already part of this configuration.
        """
        if node in self.nodes:
            raise ValueError("Node is already used in this NodeConfig")
        self.nodes.append(node)
        return True
