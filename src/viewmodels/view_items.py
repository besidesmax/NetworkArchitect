from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class NodeViewItem:
    """Node data for game field visualization."""
    node_id: int
    x: int
    y: int
    max_connections: int
    min_connections: int
    current_connections: int
    node_type: str


@dataclass
class BridgeViewItem:
    """Bridge data for connection path visualization."""
    bridge_id: int
    from_node_id: int
    to_node_id: int
    bridge_type: str
    grid_points: List[Tuple[int, int]]
