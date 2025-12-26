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
            return False

        try:
            # Delegate the actual bridge creation and validation to the Network model.
            self.network.add_bridge(from_node, grid_points, to_node, bridge_type)

            # Deduct the cost of the placed bridge from the session's current budget.
            self.current_budget = self.current_budget - bridge_type.cost
        except ValueError:
            return False
        return True

    def remove_bridge(self, bridge: Bridge) -> bool:
        """GR-04+GR-15: Removes bridge and refunds budget if exists in network.

        Args:
            bridge: Bridge instance to remove

        Returns:
            True if bridge removed and budget refunded, False otherwise.
        """

        # Delegate the actual bridge deletion to the Network model.
        try:
            self.network.delete_bridge(bridge)
        except ValueError:
            return False

        # Refund the bridge cost to the session's current budget.
        self.current_budget += bridge.bridge_type.cost

        return True

    def is_it_solved(self) -> bool:
        """GR-05+GR-09: Validates complete server-reachable network.
       Returns:
           True if GR-05 (all nodes reachable) AND GR-09 (server ≥2 conn)
        """

        # Check 1: GR-05 All level nodes present in network
        nodes_level = self.level.node_config.nodes
        nodes_network = self.network.nodes
        if set(nodes_level) != set(nodes_network):
            return False

        # Check 2: GR-09 Server minimum 2 connections
        server = self.network.get_server()
        if server.current_connections < 2:
            return False

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
            return False

        self.network.is_solved = True
        return True
