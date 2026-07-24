from itertools import chain, combinations

from network_architect.models.bridge import Bridge
from network_architect.models.bridge_type import BridgeType
from network_architect.models.grid_point import GridPoint
from network_architect.models.level import Level
from network_architect.models.network import Network
from network_architect.models.node import Node
from network_architect.models.player import Player


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

        # Network will later hold all nodes and bridges for this session.
        self.network = Network()

    def place_bridge(self, from_node: Node, grid_points: list[GridPoint], to_node: Node,
                     bridge_type: BridgeType) -> bool:
        """Place a new bridge as a player action and update the session budget.

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
            raise ValueError("Insufficient budget")

        try:
            # Delegate the actual bridge creation and validation to the Network model.
            self.network.add_bridge(from_node, grid_points, to_node, bridge_type)

            # Deduct the cost of the placed bridge from the session's current budget.
            self.current_budget = self.current_budget - bridge_type.cost
        except ValueError:
            raise
        return True

    def remove_bridge(self, bridge: Bridge) -> bool:
        """Remove a bridge from the session network and refund its cost.

        Args:
            bridge: Bridge instance to remove.

        Returns:
            True if the bridge was removed successfully.

        Raises:
            ValueError: If the bridge cannot be removed from the network.
        """

        # Delegate the actual bridge deletion to the Network model.
        try:
            self.network.delete_bridge(bridge)
        except ValueError:
            raise

        # Refund the bridge cost to the session's current budget.
        self.current_budget += bridge.bridge_type.cost

        return True

    def is_it_solved(self) -> bool:
        """Check whether the current network satisfies the level solution rules.

        A network is considered solved if all level nodes are present in the
        session network, the server has at least two connections, and every
        level node is reachable from the server.

        Returns:
            True if the network is solved, otherwise False.
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
        if set(nodes_level) != set(connected_with_server):
            return False

        self.network.is_solved = True
        return True

    def create_copy(self):
        """Create a deep copy of the current game session for analysis.

        The copied session contains equivalent nodes, bridges, and level node
        configuration, but uses separate model instances. This is used for
        temporary calculations such as redundancy analysis without modifying
        the original session.

        Returns:
            GameSession: Independent copy of the current session.
        """

        old_bridge_id_counter = Bridge.id_counter
        old_node_id_counter = Node.id_counter

        Bridge.id_counter = 9000
        Node.id_counter = 9000

        test_player = Player("test_Player")
        test_level = Level(self.level.difficulty,
                           self.level.target_performance_score,
                           self.level.target_redundancy_score,
                           self.level.start_budget
                           )
        test_session = GameSession(test_player, test_level)

        for game_node in self.network.nodes:
            for test_grid_point in test_level.game_board:
                if game_node.grid_point[0].grid_point_id == test_grid_point.grid_point_id:
                    right_grid_point = test_grid_point
                    copied_node = Node([right_grid_point], game_node.node_type)
                    copied_node.node_id = game_node.node_id
                    test_session.network.add_node(copied_node)

        # Rebuild level node configuration for the copied session.
        test_level.node_config.nodes = []
        for original_node in self.level.node_config.nodes:
            for test_node in test_session.network.nodes:
                if test_node.grid_point[0].grid_point_id == original_node.grid_point[0].grid_point_id:
                    test_level.node_config.add_node(test_node)
                    break

        for game_bridge in self.network.bridges:
            game_from_node = game_bridge.from_node
            game_grid_points: list[GridPoint] = list(game_bridge.grid_points)
            game_to_node = game_bridge.to_node
            # bridge_type doesn't need a for-loop
            right_bridge_type = game_bridge.bridge_type
            right_bridge_id = game_bridge.bridge_id
            right_from_node = None
            right_to_node = None

            # gets the node in the test_frame that equals the from_node
            for test_from_node in test_session.network.nodes:
                if test_from_node.grid_point[0].grid_point_id == game_from_node.grid_point[0].grid_point_id:
                    right_from_node = test_from_node
                    break

            # gets the grid_points: list in the test_frame that equals bridge.grid_points
            right_grid_points = []
            for game_grid_point in game_grid_points:
                for test_grid_point in test_level.game_board:
                    if game_grid_point.grid_point_id == test_grid_point.grid_point_id:
                        right_grid_points.append(test_grid_point)

            # gets the node in the test_frame that equals the to_node
            for test_to_node in test_session.network.nodes:
                if test_to_node.grid_point[0].grid_point_id == game_to_node.grid_point[0].grid_point_id:
                    right_to_node = test_to_node
                    break

            test_session.place_bridge(right_from_node, right_grid_points, right_to_node, right_bridge_type)
            right_bridge = test_session.network.find_bridge_by_path(right_from_node, right_to_node, right_grid_points)

            if right_bridge is None:
                raise ValueError("Copied bridge not found in test session")

            right_bridge.bridge_id = right_bridge_id

        Bridge.id_counter = old_bridge_id_counter
        Node.id_counter = old_node_id_counter

        return test_session

    def calculate_redundancy_score(self) -> int:
        """Calculate the redundancy score for the current network.

        The redundancy score is defined as the number of non-empty bridge
        subsets that can be removed while the network still satisfies the
        solution rules (all level nodes reachable and server connected).

        The method tests all non-empty subsets of existing bridges by
        temporarily removing them in a copied session and re-validating
        the network.

        Raises:
            ValueError: If the network is not solved before the calculation.

        Returns:
            int: Number of redundant bridge subsets.
        """

        # Precondition: Network must be solved
        if self.is_it_solved() is False:
            raise ValueError("Network must be solved before redundancy calculation")

        # Stable copy for exhaustive testing (iteration-safe)
        redundancy_score = 0

        # Create stable copy of current bridges
        original_bridges = list(self.network.bridges)

        # Generate all non-empty subsets (Power Set - empty set)
        def all_subsets(bridges):
            return chain(*[combinations(bridges, r) for r in range(1, len(bridges) + 1)])

        # Test each possible bridge subset removal
        for subset in all_subsets(original_bridges):
            test_session = self.create_copy()

            # Phase 1: Remove all bridges in current subset
            for bridge in subset:
                test_bridge = None
                for candidate in test_session.network.bridges:
                    if candidate.bridge_id == bridge.bridge_id:
                        test_bridge = candidate
                        break

                if test_bridge is None:
                    raise ValueError("Bridge for redundancy test not found in copied network")

                test_session.network.delete_bridge(test_bridge)

            # Phase 2: Test if network remains solved without this subset
            try:
                if test_session.is_it_solved() is True:
                    redundancy_score += 1
            except ValueError:
                pass

            # Phase 3: Restore exact original state
            test_session = self.create_copy()

        # Store result for MVVM data binding and return
        self.network.redundancy_score = redundancy_score
        return redundancy_score

    def calculate_performance(self):
        """
        Calculate network performance score per GR-13.

        Computes average bottleneck bandwidth (min per path, max per node)
        across all client nodes (excludes server). Network must be solved.

        Raises:
            ValueError: If network is not solved (GR-05 violated).

        Returns:
            float: Performance score (avg bottleneck BW in arbitrary units).
        """

        # Precondition: Network must be solved
        if not self.is_it_solved():
            raise ValueError("Network must be solved before performance calculation")

        network_bandwidth: list[int] = []

        # Iterate over all nodes, calculate max bottleneck per node
        for node in self.network.nodes:
            node_bandwidth: list[int] = []
            for path in self.network.find_path(node):
                path_bandwidth = []
                for bridge in path:
                    path_bandwidth.append(bridge.bridge_type.bandwidth)

                if path_bandwidth:
                    # Bottleneck = min bandwidth on path (GR-13)
                    node_bandwidth.append(min(path_bandwidth))

            if node_bandwidth:
                # Best path for this node = max over path bottlenecks
                network_bandwidth.append(max(node_bandwidth))

        total_bandwidth = sum(network_bandwidth)
        # Exclude server node (GR-08: exactly 1 server)
        num_node = len(self.network.nodes) - 1
        performance_score = total_bandwidth / num_node

        self.network.performance_score = performance_score

        return performance_score
