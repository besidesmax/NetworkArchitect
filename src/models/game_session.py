from models.level import Level
from models.player import Player
from models.network import Network
from models.node import Node
from models.grid_point import GridPoint
from models.bridge_type import BridgeType
from models.bridge import Bridge


class GameSession:
    """Represents a single game session for one player and one level."""
    id_counter = 0  # Simple in-memory counter to assign unique GameSession IDs.

    def __init__(self, player: Player, level: Level) -> None:
        """Create a new game session with an initial budget.

        Args:
            player: Player profile associated with this session.
            level: Level that is played in this session.
        """
        # Assign a unique ID to this game session instance.
        self.game_session_id = GameSession.id_counter
        GameSession.id_counter += 1
        self.player = player
        self.level = level

        # Start each session with the level's initial budget.
        self.current_budget = level.start_budget

        # Network will later hold all nodes and bridges for this level.
        self.network = Network()

    def place_bridge(self, from_node: Node, grid_points: list[GridPoint], to_node: Node,
                     bridge_type: BridgeType) -> bool:
        """
            Place a new bridge as a player action and update the session budget.
        Args:
            from_node: Start node of the bridge.
            grid_points: Grid points the bridge will occupy between the nodes.
            to_node: End node of the bridge.
            bridge_type: Type of the bridge to be placed.

        Returns:
            True if the bridge was successfully placed and the budget updated.

        Raises:
            ValueError: If the current budget is lower than the required bridge cost.
        """

        # Ensure that the player has enough budget for this bridge placement.
        if self.current_budget < bridge_type.cost:
            raise ValueError(f"Current budge ist to low; current = {self.current_budget}; cost = {bridge_type.cost}")
        # Delegate the actual bridge creation and validation to the Network model.
        self.network.add_bridge(from_node, grid_points, to_node, bridge_type)
        # Deduct the cost of the placed bridge from the session's current budget.
        self.current_budget = self.current_budget - bridge_type.cost

        return True

    def remove_bridge(self, bridge: Bridge) -> bool:
        """
            Remove an existing bridge as a player action and update the session budget.
        Args:
            bridge: The bridge instance to remove from the network.

        Returns:
            bool: True if the bridge was successfully removed and the budget.
        """

        # Delegate the actual bridge deletion to the Network model.
        self.network.delete_bridge(bridge)

        # Refund the bridge cost to the session's current budget.
        self.current_budget = self.current_budget + bridge.bridge_type.cost

        return True

    def is_it_solved(self) -> None:
        """GR-05+GR-09: Complete server-reachable network?
        Returns:
        True if all level nodes exist, server has ≥2 connections,
        and all nodes are server-reachable.
        """

        # Check 1: GR-05 All level nodes present in network
        nodes_level = self.level.node_config.nodes
        nodes_network = self.network.nodes
        if set(nodes_level) != set(nodes_network):
            raise ValueError("Not all nodes connected to an other node")

        # Check 2: GR-09 Server minimum 2 connections
        server = self.network.get_server()
        if not server.current_connections >= 2:
            raise ValueError(f"Server has only {server.current_connections}; need 2 or more")

        # Check 3: GR-05 BFS reachability from server
        connected_with_server = [server]

        def add_nodes_connected_to_server() -> bool:
            """BFS iteration: Expands visited set with directly connected nodes.

            Returns:
                True if new nodes were added (continue BFS)
            """
            nodes_added = False

            # first direction: from_node → to_node
            for bridge in self.network.bridges:
                if (bridge.from_node in connected_with_server and
                        bridge.to_node not in connected_with_server):
                    connected_with_server.append(bridge.to_node)
                    nodes_added = True

            # second direction: to_node → from_node
            for bridge in self.network.bridges:
                if (bridge.to_node in connected_with_server and
                        bridge.from_node not in connected_with_server):
                    connected_with_server.append(bridge.from_node)
                    nodes_added = True

            return nodes_added

        while add_nodes_connected_to_server():
            pass

        # Check 4: GR-05 All nodes server-reachable?
        if set(nodes_network) != set(connected_with_server):
            raise ValueError("not all Nodes connected with server")

        self.network.is_solved = True
        return
