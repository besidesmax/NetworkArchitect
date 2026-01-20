import pytest
from models.node import Node
from models.node_type import NodeType
from models.grid_point import GridPoint


@pytest.mark.parametrize("node_type", NodeType)
def test_add_connections(node_type: NodeType) -> None:
    """
    Tests Node.add_connection() for all NodeTypes:

    - Success: current_connections increases by 1 when result=True
    - Limit: current_connections unchanged when result=False (max reached)
    """
    grid_point1 = GridPoint(1, 1)
    node = Node([grid_point1], node_type=node_type)
    start = node.current_connections

    for attempt in range(node.node_type.max_connections):
        node.add_connection()
        assert node.current_connections == start + (attempt + 1)
    # one more attempt must raise a ValueError
    with pytest.raises(ValueError):
        node.add_connection()


@pytest.mark.parametrize("node_type", NodeType)
def test_remove_connections(node_type: NodeType) -> None:
    """
#     Test Node.remove_connection() for all NodeTypes.
#
#     The test verifies two behaviors:
#     - Normal case: current_connections decreases by 1 while it is > 0.
#     - Lower bound: current_connections never drops below 0.
#     """

    grid_point1 = GridPoint(1, 1)
    node = Node([grid_point1], node_type=node_type)

    for attempt in range(node.node_type.max_connections):
        node.add_connection()

    start = node.current_connections

    for attempt in range(node.current_connections):
        node.remove_connection()
        assert node.current_connections == start - (attempt + 1)

    # one more attempt must raise a ValueError
    with pytest.raises(ValueError):
        node.remove_connection()
