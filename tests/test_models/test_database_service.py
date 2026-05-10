"""Unit tests for DatabaseService."""

import pytest

from models.database_service import DatabaseService
from models.difficulty import Difficulty
from models.node_type import NodeType


@pytest.fixture
def db_service():
    """Create a completely fresh, isolated in-memory database for each test."""
    db = DatabaseService(db_path=":memory:")

    return db


class TestPlayerOperations:
    """Tests for player-related database operations."""

    def test_create_player_success(self, db_service: DatabaseService):
        """
         Test successfully creating a valid player.

        Verifies that:
        - A player can be created without raising an exception.
        - The player is correctly persisted in the database.
        - An integer player_id is assigned by the database.
        - The name is stored exactly as provided.
        """

        db_service.create_player("test_player")

        test_player = db_service.get_player_by_name("test_player")

        assert test_player is not None
        assert isinstance(test_player.player_id, int)
        assert test_player.name == "test_player"

    def test_create_player_empty_name(self, db_service: DatabaseService):
        """
        Test that creating a player with an empty name fails.

        Verifies that the database service strictly enforces the minimum
        length requirement (2-20 characters) and rejects empty strings.
        """

        with pytest.raises(ValueError):
            db_service.create_player("")

    def test_create_player_too_short(self, db_service: DatabaseService):
        """
        Test that creating a player with a too short name fails.

        Verifies that the database service strictly enforces the minimum
        length requirement (2-20 characters) and rejects strings with
        less than 2 characters.
        """

        with pytest.raises(ValueError):
            db_service.create_player("A")

    def test_create_player_too_long(self, db_service: DatabaseService):
        """
        Test that creating a player with a too long name fails.

        Verifies that the database service strictly enforces the maximum
        length allowed (2-20 characters) and rejects strings with
        more than 20 characters.
        """

        with pytest.raises(ValueError):
            db_service.create_player("A" * 21)

    def test_create_player_duplicate(self, db_service: DatabaseService):
        """
        Test that creating a player with an existing name fails.

        Verifies that the database enforces the UNIQUE constraint on player names
        and raises a ValueError instead of throwing a generic database error.
        """
        # Create the initial player successfully
        db_service.create_player("test_player")

        # Attempting to create another player with the exact same name must fail
        with pytest.raises(ValueError):
            db_service.create_player("test_player")

    def test_get_player_by_name(self, db_service: DatabaseService):
        """
       Test retrieving a player by their name.

       Verifies three scenarios:
       1. Successfully retrieving an existing player.
       2. Returning None for invalid names (e.g., too short).
       3. Returning None when the player does not exist in the database.
       """

        # Create a player in the database
        player = db_service.create_player("test_player")

        # Act & Assert 1: Player exists (verify attributes, not memory address)
        assert db_service.get_player_by_name("test_player").name == player.name

        # Act & Assert 2: Invalid name (less than 2 characters)
        assert db_service.get_player_by_name("a") is None

        # Act & Assert 3: Valid name, but player not found
        assert db_service.get_player_by_name("1Test_player") is None

    def test_get_player_by_id(self, db_service: DatabaseService):
        """
        Test retrieving a player by their database ID.

        Verifies that:
        1. An existing player is retrieved correctly.
        2. Passing an invalid type (e.g., string) raises ValueError.
        3. Passing zero or negative IDs raises ValueError.
        4. Passing an ID that does not exist raises ValueError.
        """

        # Create a player in the database and get their player_id
        db_service.create_player("test_player")
        player_id = db_service.get_player_by_name("test_player").player_id
        retrieved_player = db_service.get_player_by_id(player_id)

        # Act & Assert 1: Success case
        assert retrieved_player.name == "test_player"
        assert retrieved_player.player_id == player_id

        # Act & Assert 2: Invalid type (string instead of int)
        with pytest.raises(ValueError):
            db_service.get_player_by_id("a")

        # Act & Assert 3: Invalid value (<= 0)
        with pytest.raises(ValueError):
            db_service.get_player_by_id(0)

        with pytest.raises(ValueError):
            db_service.get_player_by_id(-1)

        # Act & Assert 4: ID not found (999 is safely non-existent in fresh DB)
        with pytest.raises(ValueError):
            db_service.get_player_by_id(999)

    def test_get_all_players(self, db_service: DatabaseService):
        """
        Test retrieving all players from the database.

        Verifies that:
        1. An empty database returns an empty list.
        2. A populated database returns all players correctly.
        """

        # Act & Assert 1: Empty database
        assert db_service.get_all_players() == []

        # Arrange: Create multiple players
        db_service.create_player("eins")
        db_service.create_player("zwei")
        player_1 = db_service.get_player_by_name("eins")
        player_2 = db_service.get_player_by_name("zwei")

        # Act: Retrieve all players
        player_list_object = db_service.get_all_players()

        # List comprehension to check if the names and ids are correct
        player_list_db_names = [player_list_object[0].name,
                                player_list_object[0].player_id,
                                player_list_object[1].name,
                                player_list_object[1].player_id]

        player_list_assert = [player_1.name,
                              player_1.player_id,
                              player_2.name,
                              player_2.player_id]

        assert player_list_db_names == player_list_assert


class TestLevelOperations:
    """Tests for level-related database operations."""

    # Shared test data: minimal valid node configuration for level creation
    VALID_NODE_CONFIG = ('[{"grid_point_id": 2, "node_type": "CLIENT"},'
                         ' {"grid_point_id": 5, "node_type": "SERVER"}]')

    def test_create_level_success(self, db_service: DatabaseService):
        """
        Test successfully creating a valid level.

        Verifies that:
        - The level is persisted and retrievable from the database.
        - All metadata (difficulty, scores, budget) is stored correctly.
        - Node configuration is correctly reconstructed from JSON.
        """

        # Act: Create level and capture returned instance
        level_created = db_service.create_level(Difficulty.MEDIUM,
                                                500,
                                                500,
                                                5000,
                                                self.VALID_NODE_CONFIG)

        assert level_created.level_id is not None

        # Assert: Retrieve from DB and verify all attributes

        level_id = level_created.level_id
        level = db_service.get_level(level_id)

        assert level.difficulty == Difficulty.MEDIUM
        assert level.target_performance_score == 500
        assert level.target_redundancy_score == 500
        assert level.start_budget == 5000

        # Assert: Node config was correctly reconstructed from JSON
        assert level.node_config.nodes[0].grid_point[0].grid_point_id == 2
        assert level.node_config.nodes[0].node_type == NodeType.CLIENT
        assert level.node_config.nodes[1].grid_point[0].grid_point_id == 5
        assert level.node_config.nodes[1].node_type == NodeType.SERVER

    def test_create_level_invalid_node_config(self, db_service: DatabaseService):
        """
        Test that creating a level with an invalid node config fails.

        Verifies that the database service raises a ValueError for:
        1. Empty strings as node configuration.
        2. Empty JSON arrays (no nodes defined).
        3. Malformed JSON strings that cannot be parsed.
        """

        # Act & Assert 1: Empty string is rejected immediately
        with pytest.raises(ValueError):
            db_service.create_level(Difficulty.MEDIUM,
                                    500,
                                    500,
                                    5000,
                                    '')

        # Act & Assert 2: Empty JSON array is rejected (no nodes defined)
        with pytest.raises(ValueError):
            db_service.create_level(Difficulty.MEDIUM,
                                    500,
                                    500,
                                    5000,
                                    '[]')

        # Act & Assert 3: Malformed JSON string raises ValueError
        with pytest.raises(ValueError):
            db_service.create_level(Difficulty.MEDIUM,
                                    500,
                                    500,
                                    5000,
                                    'das ist kein json {')

    def test_get_level_success(self, db_service: DatabaseService):
        """
        Test successfully retrieving a level by its ID.

        Verifies that all level metadata and node configuration
        are correctly reconstructed from the database.
        """
        # Arrange: Create a level to retrieve
        level_created = db_service.create_level(Difficulty.MEDIUM,
                                                500,
                                                500,
                                                5000,
                                                self.VALID_NODE_CONFIG)

        # Act: Retrieve the level by its assigned ID
        level_id = level_created.level_id
        get_level = db_service.get_level(level_id)
        assert get_level.level_id == level_id

        # Assert: Verify all metadata matches
        assert get_level.difficulty == level_created.difficulty
        assert get_level.target_redundancy_score == level_created.target_redundancy_score
        assert get_level.target_performance_score == level_created.target_performance_score
        assert get_level.start_budget == level_created.start_budget

        # Assert: Verify node config was correctly
        assert get_level.node_config.nodes[0].node_type == level_created.node_config.nodes[0].node_type
        assert get_level.node_config.nodes[0].grid_point[0].grid_point_id == \
               level_created.node_config.nodes[0].grid_point[0].grid_point_id
        assert get_level.node_config.nodes[1].node_type == level_created.node_config.nodes[1].node_type
        assert get_level.node_config.nodes[1].grid_point[0].grid_point_id == \
               level_created.node_config.nodes[1].grid_point[0].grid_point_id

    def test_get_level_invalid_cases(self, db_service: DatabaseService):
        """
        Test that retrieving a level with invalid IDs raises a ValueError.

        Verifies that the database service rejects:
        1. Non-positive IDs (0, negative) before any database interaction.
        2. Valid-looking IDs that do not exist in the database.
        """

        # Act & Assert 1: Zero is not a valid ID
        with pytest.raises(ValueError):
            db_service.get_level(0)

        # Act & Assert 2: Negative IDs are rejected immediately
        with pytest.raises(ValueError):
            db_service.get_level(-1)

        # Act & Assert 3: Valid-looking ID that does not exist in DB
        with pytest.raises(ValueError):
            db_service.get_level(500)

    def test_get_all_levels_success(self, db_service: DatabaseService):
        """
        Test retrieving all levels in both empty and populated database states.

        Verifies that:
        1. An empty database returns an empty list without raising an exception.
        2. All created levels are returned ordered alphabetically by difficulty.
        """
        # Act & Assert 1: Empty database returns empty list
        levels = db_service.get_all_levels()
        assert levels == []

        # Arrange: Create three levels with different difficulties
        db_service.create_level(Difficulty.MEDIUM,
                                500,
                                500,
                                5000,
                                self.VALID_NODE_CONFIG)

        db_service.create_level(Difficulty.HARD,
                                500,
                                500,
                                5000,
                                self.VALID_NODE_CONFIG)

        db_service.create_level(Difficulty.LIGHT,
                                500,
                                500,
                                5000,
                                self.VALID_NODE_CONFIG)

        levels = db_service.get_all_levels()

        # Act & Assert 2: All levels returned in alphabetical difficulty order
        assert levels[0].difficulty == Difficulty.HARD
        assert levels[1].difficulty == Difficulty.LIGHT
        assert levels[2].difficulty == Difficulty.MEDIUM

    def test_update_level_success(self, db_service: DatabaseService):
        """
        Test that updating all supported level columns works correctly.

        Verifies that difficulty, target_redundancy_score,
        target_performance_score, and start_budget can be updated
        and are correctly persisted in the database.
        """
        # Arrange: Create a level to update
        db_service.create_level(Difficulty.MEDIUM,
                                500,
                                500,
                                5000,
                                self.VALID_NODE_CONFIG)

        # Act: Update all supported columns
        db_service.update_level(1, "difficulty", Difficulty.HARD)
        db_service.update_level(1, "target_redundancy_score", 800)
        db_service.update_level(1, "target_performance_score", 800)
        db_service.update_level(1, "start_budget", 50000)

        # Assert: All updates are reflected in the returned level
        level = db_service.get_level(1)
        assert level.difficulty == Difficulty.HARD
        assert level.target_redundancy_score == 800
        assert level.target_performance_score == 800
        assert level.start_budget == 50000

    def test_update_level_invalid_cases(self, db_service: DatabaseService):
        """
        Test that update_level raises ValueError for invalid inputs.

        Verifies rejection of:
        1. Invalid column names not in the allowed set.
        2. Non-existent level IDs.
        3. Non-positive level IDs (0, negative).
        4. Wrong value type for a column (negative int for score).
        """
        # Arrange: Create a level to update
        db_service.create_level(Difficulty.MEDIUM,
                                500,
                                500,
                                5000,
                                self.VALID_NODE_CONFIG)

        # Act & Assert 1: Invalid column name is rejected
        with pytest.raises(ValueError):
            db_service.update_level(1, "wrong_column", 522)

        # Act & Assert 2: Non-existent level ID raises ValueError
        with pytest.raises(ValueError):
            db_service.update_level(5, "start_budget", 522)

        # Act & Assert 3: Non-positive level ID is rejected immediately
        with pytest.raises(ValueError):
            db_service.update_level(0, "start_budget", 522)

        # Act & Assert 4: Negative value for score column is rejected
        with pytest.raises(ValueError):
            db_service.update_level(1, "start_budget", -522)

    def test_delete_level_success(self, db_service: DatabaseService):
        """
        Test that a level is successfully deleted from the database.

        Verifies that after deletion, attempting to retrieve
        the level raises a ValueError.
        """
        # Arrange: Create a level to delete
        db_service.create_level(Difficulty.MEDIUM,
                                500,
                                500,
                                5000,
                                self.VALID_NODE_CONFIG)

        # Act: Delete the level
        db_service.delete_level(1)

        # Assert: Level no longer exists in the database
        with pytest.raises(ValueError):
            db_service.get_level(1)

    def test_delete_level_invalid_cases(self, db_service: DatabaseService):
        """
        Test that delete_level raises ValueError for invalid inputs.

        Verifies rejection of:
        1. Non-positive level IDs (0, negative).
        2. Valid-looking IDs that do not exist in the database.
        """
        # Act & Assert 1: Non-positive ID is rejected immediately
        with pytest.raises(ValueError):
            db_service.delete_level(-1)

        with pytest.raises(ValueError):
            db_service.delete_level(0)

        # Act & Assert 2: Non-existent level ID raises ValueError
        with pytest.raises(ValueError):
            db_service.delete_level(999)
