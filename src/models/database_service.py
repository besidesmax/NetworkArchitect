import os
import sqlite3
from models.player import Player


class DatabaseService:
    """Manages SQLite persistence for Network Architect game sessions."""

    def __init__(self) -> None:
        self.db_path = os.path.join(os.path.dirname(__file__), "data", "network_architect.db")
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        # Initialize database schema
        self._init_schema()

    def _init_schema(self) -> None:
        """Creates all required tables if they do not exist."""
        cursor = self.conn.cursor()

        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
    
            CREATE TABLE IF NOT EXISTS levels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                difficulty TEXT NOT NULL,  -- 'easy', 'medium', 'hard'
                node_config TEXT NOT NULL,  -- JSON: [{"x":1,"y":2,"type":"server",...}]
                target_redundancy_score INTEGER NOT NULL,
                target_performance_score INTEGER NOT NULL,
                start_budget INTEGER NOT NULL
            );
    
            CREATE TABLE IF NOT EXISTS player_completed_levels (
                player_id INTEGER NOT NULL,
                level_id INTEGER NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                achieved_redundancy INTEGER,
                achieved_performance INTEGER,
                PRIMARY KEY (player_id, level_id),
                FOREIGN KEY(player_id) REFERENCES players(id),
                FOREIGN KEY(level_id) REFERENCES levels(id)
            );
            """)

        self.conn.commit()

    def create_player(self, name: str) -> Player:
        """
        Creates a new Player with given name and persists it in database.

        Args:
            name (str): Unique player name.

        Returns:
            Player: New Player instance with assigned database ID.

        Raises:
            ValueError: If player with this name already exists.
        """
        # Validate and normalize input
        if not name or len(name.strip()) < 2 or len(name.strip()) > 20:
            raise ValueError("Player name must be 2-20 characters")
        name = name.strip()

        cursor = self.conn.cursor()

        # Check duplicate
        cursor.execute("SELECT id FROM players WHERE name = ?", (name,))
        if cursor.fetchone():
            raise ValueError("Player with this name already exists")

        # Insert and get ID
        cursor.execute("INSERT INTO players (name) VALUES (?)", (name,))
        player_id = cursor.lastrowid

        self.conn.commit()

        # Create and return Player instance
        player = Player(name)
        player.player_id = player_id

        return player
