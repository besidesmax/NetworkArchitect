from enum import Enum


class BridgeType(Enum):
    """Enumeration of all Bridge types in the game.

        Each member defines a display name, bandwidth and cost
    """

    ETHERNET = ("ETHERNET", 100, 10)
    WIFI_24G = ("WIFI_24G", 300, 20)
    WIFI_5G = ("WIFI_5G", 600, 35)
    FIBER = ("FIBER", 2000, 120)

    def __init__(self, display_name: str, bandwidth: int, cost: int):
        """Initialize a bridge type with bandwidth and cost.

                Args:
                    display_name: Human‑readable name shown in the UI.
                    bandwidth: the bandwidth of the connection.
                    cost: cost of the connection.
        """
        self.display_name = display_name
        self.bandwidth = bandwidth
        self.cost = cost
