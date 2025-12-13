from enum import Enum


class NodeType(Enum):
    """Enumeration of all network device types in the game.

        Each member defines a display name and connection constraints.
    """

    SERVER = ("SERVER", 4, 2)
    CLIENT = ("CLIENT", 4, 0)
    ROUTER = ("ROUTER", 4, 0)
    FIREWALL = ("FIREWALL", 2, 0)

    def __init__(self, display_name: str, max_connections: int, min_connections: int):
        """Initialize a node type with connection limits.

                Args:
                    display_name: Human‑readable name shown in the UI.
                    max_connections: Maximum allowed connections for this type.
                    min_connections: Minimum required connections for this type.
        """
        self.display_name = display_name
        self.max_connections = max_connections
        self.min_connections = min_connections
