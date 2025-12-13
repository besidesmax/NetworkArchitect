from NodeType import NodeType


class Node:
    """Die Nodes sind die Netzwerkdevices im Spiel"""

    def __init__(self, node_id: int, x: int, y: int, node_type: NodeType):
        self.node_id = node_id
        self.positionX = x
        self.positionY = y
        self.node_type = node_type
        self.current_connections = 0
        self.max_connections = node_type.max_connections

    def add_connection(self) -> bool:
        """Fügt eine Brückenverbindung hinzu (GR-06).

            Returns:
                True wenn erfolgreich, False wenn Kapazität voll.
        """
        if self.current_connections >= self.max_connections:
            return False
        self.current_connections += 1
        return True


