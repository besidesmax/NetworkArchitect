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

    def test_create_player_duplicate(self, db_service):
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

#    def test_get_player_by_name_not_found(self, db_service):

#       db_service.create_player("test_player_1")
