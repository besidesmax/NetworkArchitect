import pytest

from models.grid_point import GridPoint
from models.node import Node
from models.node_config import NodeConfig
from models.node_type import NodeType


def test_node_config():
    """
    Test successfully adding a node to a NodeConfig.

    Verifies that:
    - The method returns True on successful insertion.
    - The node is present in the nodes list after adding.
    """
    # Arrange
    node_config = NodeConfig()
    gp = GridPoint(1, 1)
    node = Node([gp], NodeType.CLIENT)

    # Act
    result = node_config.add_node(node)

    # Assert
    assert result is True
    assert node in node_config.nodes


def test_add_node_raises_on_duplicate():
    """
    Test that adding the same node twice raises a ValueError.

    Verifies that the NodeConfig enforces uniqueness
    and raises ValueError when a duplicate node is added.
    """
    # Arrange
    node_config = NodeConfig()
    gp = GridPoint(1, 1)
    node = Node([gp], NodeType.CLIENT)
    node_config.add_node(node)

    # Act & Assert
    with pytest.raises(ValueError):
        node_config.add_node(node)
