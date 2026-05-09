"""Unit tests for DatabaseService."""

import pytest
import sqlite3
from models.database_service import DatabaseService


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

        # List comprehension to check if the names and id's are correct
        player_list_db_names = [player_list_object[0].name,
                                player_list_object[0].player_id,
                                player_list_object[1].name,
                                player_list_object[1].player_id]

        player_list_assert = [player_1.name,
                              player_1.player_id,
                              player_2.name,
                              player_2.player_id]

        assert player_list_db_names == player_list_assert
