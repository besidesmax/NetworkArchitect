import pytest

from models.node import Node
from models.node_type import NodeType


@pytest.mark.parametrize("node_type", NodeType)
def test_add_connections(node_type: NodeType) -> None:
    """
    Tests Node.add_connection() for all NodeTypes:

    - Success: current_connections increases by 1 when result=True
    - Limit: current_connections unchanged when result=False (max reached)
    """

    node = Node(1, 1, 1, node_type=node_type)
    start = node.current_connections

    for attempt in range(1, 8):
        result = node.add_connection()

        if result:
            assert (
                    node.current_connections == start + attempt), \
                f"Expected {start + attempt}, got {node.current_connections}"
        else:
            expected_max = start + (attempt - 1)
            assert (
                    node.current_connections == expected_max), \
                f"Expected no increase at max ({expected_max}), got {node.current_connections}"
            assert (
                    node.current_connections <= node.node_type.max_connections), \
                f"Max exceeded: {node.current_connections} > {node.node_type.max_connections}"
            break
