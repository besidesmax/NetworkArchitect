import json
import os
import sqlite3
from typing import List, Dict, Any

from models.difficulty import Difficulty
from models.level import Level
from models.node import Node
from models.node_type import NodeType
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
                node_config TEXT NOT NULL,
                target_redundancy_score INTEGER NOT NULL,
                target_performance_score INTEGER NOT NULL,
                start_budget INTEGER NOT NULL
            );
    
            CREATE TABLE IF NOT EXISTS player_completed_levels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                level_id INTEGER NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                elapsed_time_seconds INTEGER,
                achieved_redundancy INTEGER,
                achieved_performance INTEGER,
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

    def get_player_by_name(self, name: str) -> Player | None:
        """
        Retrieves a Player by name from the database.

        Args:
            name (str): Player name to lookup.

        Returns:
            Player | None: Player instance if found, None otherwise.
        """
        # Validate input
        if not name or len(name.strip()) < 2:
            return None

        name = name.strip()

        cursor = self.conn.cursor()

        # Fetch player by name (parameterized query)
        cursor.execute("SELECT id, name FROM players WHERE name = ?", (name,))
        row = cursor.fetchone()

        if row is None:
            return None

        # Reconstruct Player instance from database row
        player_id, player_name = row
        player = Player(name=player_name)
        player.player_id = player_id

        return player

    def get_player_by_id(self, player_id: int) -> Player:
        """
        Retrieve a Player by ID from the database.

        Args:
            player_id: Primary key of the player to fetch.

        Returns:
            Player instance if found.

        Raises:
            ValueError: If player_id is invalid or not found in database.
        """
        # Validate input
        if not isinstance(player_id, int) or player_id <= 0:
            raise ValueError("player_id must be a positive integer")

        cursor = self.conn.cursor()

        # Fetch player by ID (parameterized query)
        cursor.execute("SELECT id, name FROM players WHERE id = ?", (player_id,))
        row = cursor.fetchone()

        if row is None:
            raise ValueError(f"Player ID {player_id} not found in database")

        # Reconstruct Player instance from database row
        player_id, player_name = row
        player = Player(name=player_name)
        player.player_id = player_id

        return player

    def get_all_players(self) -> List[Player]:
        """Retrieve all players from database for selection screen."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM players ORDER BY name")
        rows = cursor.fetchall()

        players = []
        for row in rows:
            player_id, name = row
            player = Player(name)
            player.player_id = player_id
            players.append(player)

        return players

    def create_level(self, difficulty: Difficulty, target_performance_score: int,
                     target_redundancy_score: int, start_budget: int, node_config_json: str) -> Level:
        """Create new level and persist to database.

        Args:
            difficulty: Game difficulty level enum.
            target_performance_score: Target score for performance metric.
            target_redundancy_score: Target score for redundancy metric.
            start_budget: Player starting resource budget.
            node_config_json: JSON array of nodes
                e.g. '[{"grid_point_id":2,"node_type":"CLIENT"}]'

        Raises:
            ValueError: Invalid JSON, missing fields, or unknown grid points.
            json.JSONDecodeError: Malformed JSON string.

        Returns:
            Level instance with populated nodes from JSON config.
        """
        # Validate JSON input
        if not node_config_json.strip():
            raise ValueError("node_config_json cannot be empty")

        try:
            data: List[Dict[str, Any]] = json.loads(node_config_json)
            if not isinstance(data, list) or len(data) == 0:
                raise ValueError("node_config_json must be non-empty node array")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}") from e

        cursor = self.conn.cursor()

        # Persist level metadata
        cursor.execute("""
                INSERT INTO levels (
                    difficulty, node_config, target_redundancy_score,
                    target_performance_score, start_budget
                ) VALUES (?, ?, ?, ?, ?)
            """, (
            difficulty.display_name,
            node_config_json,
            target_redundancy_score,
            target_performance_score,
            start_budget
        ))

        level = Level(difficulty, target_performance_score, target_redundancy_score, start_budget)
        level_id = cursor.lastrowid
        level.level_id = level_id

        self.conn.commit()

        # Reconstruct NodeConfig from JSON
        for node_data in data:
            node_grid_point_id: int = node_data["grid_point_id"]

            # Locate GridPoint by ID
            node_grid_point = None
            for level_grid_point in level.game_board:
                if level_grid_point.grid_point_id == node_grid_point_id:
                    node_grid_point = level_grid_point
                    break

            # create Node and add to NodeConfig
            if node_grid_point is None:
                raise ValueError(f"GridPoint ID {node_grid_point_id} not found")

            node_type_enum = NodeType[node_data["node_type"]]
            level.node_config.add_node(Node([node_grid_point], node_type_enum))

        return level

    def get_level(self, level_id: int) -> Level:
        """Retrieve level from database by ID.

        Args:
            level_id: Primary key of level in database.

        Raises:
            ValueError: Level ID not found in database.

        Returns:
            Level with nodes, game_board, and metadata.
        """
        if level_id <= 0:
            raise ValueError("level_id must be positive integer")

        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT difficulty, node_config, target_redundancy_score, "
            "target_performance_score, start_budget FROM levels WHERE id = ?",
            (level_id,)
        )

        row = cursor.fetchone()
        if row is None:
            raise ValueError(f"Level ID {level_id} not found")

        # Parse metadata
        difficulty = Difficulty[row[0]]
        node_config_json = row[1]
        target_perf = row[2]
        target_red = row[3]
        start_budget = row[4]

        # Reconstruct Level
        level = Level(difficulty, target_perf, target_red, start_budget)
        level.level_id = level_id

        # Reconstruct Node
        data: List[Dict[str, Any]] = json.loads(node_config_json)
        for node_data in data:
            node_grid_point_id: int = node_data["grid_point_id"]

            node_grid_point = None
            for grid_point in level.game_board:
                if grid_point.grid_point_id == node_grid_point_id:
                    node_grid_point = grid_point
                    break

            if node_grid_point is None:
                raise ValueError(f"GridPoint ID {node_grid_point_id} not found")

            node_type_enum = NodeType[node_data["node_type"]]
            level.node_config.add_node(Node([node_grid_point], node_type_enum))

        return level

    def get_all_levels(self) -> List[Level]:
        """
        Retrieve all levels from the database for level selection screen.

        Returns all levels ordered by difficulty, with populated node_config
        and game_board for UI display.

        Returns:
            List of all Level instances ordered by difficulty and id.

        Raises:
            ValueError: If a level cannot be loaded or JSON parsing fails.
        """
        cursor = self.conn.cursor()

        # Fetch all level IDs ordered by difficulty and id
        cursor.execute("SELECT id FROM levels ORDER BY difficulty, id")
        rows = cursor.fetchall()  # ← Nur IDs aus DB!

        levels = []
        for row in rows:
            level_id = row[0]
            level = self.get_level(level_id)
            levels.append(level)

        return levels

    def delete_level(self, level_id: int) -> None:
        """Delete level from database by ID.

        Args:
            level_id: Primary key of level to delete.

        Raises:
            ValueError: Level ID not found or invalid.
        """
        if level_id <= 0:
            raise ValueError("level_id must be positive integer")

        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM levels WHERE id = ?", (level_id,))

        if cursor.rowcount == 0:
            raise ValueError(f"Level ID {level_id} not found")

        self.conn.commit()

    def update_level(self, level_id: int, column: str, value: Any) -> Level:
        """Update single column of level by ID.

        Args:
            level_id: Primary key of level to update.
            column: Column name ('difficulty', 'target_performance_score', etc.).
            value: New value (str for difficulty, int for scores/budget).

        Raises:
            ValueError: Invalid level_id, column, or value type.
            sqlite3.IntegrityError: Database constraint violation.

        Returns:
            Updated Level instance (fresh from DB).
        """
        if level_id <= 0:
            raise ValueError("level_id must be positive integer")

        valid_columns = {
            'difficulty', 'target_redundancy_score',
            'target_performance_score', 'start_budget'
        }

        if column not in valid_columns:
            raise ValueError(f"Invalid column '{column}'. Valid: {valid_columns}")

        # Type validation
        if column == 'difficulty':
            try:
                Difficulty(value)
            except ValueError:
                raise ValueError(f"Invalid difficulty: '{value}'")
            value = Difficulty(value).display_name
        elif column in ('target_redundancy_score', 'target_performance_score', 'start_budget'):
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"{column} must be non-negative integer")

        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE levels SET {column} = ? WHERE id = ?",
            (value, level_id)
        )

        if cursor.rowcount == 0:
            raise ValueError(f"Level ID {level_id} not found")

        self.conn.commit()

        # Return fresh instance
        return self.get_level(level_id)

    def get_player_completed_levels(self, player_id: int) -> List[Dict[str, Any]]:
        """
        Retrieve all completed levels for a specific player.

        Args:
            player_id: Player ID to query.

        Returns:
            List of dicts with level_id, completion_time, and scores.
            Empty list if player has no completed levels.

        Raises:
            ValueError: If player_id is invalid.
        """
        if not isinstance(player_id, int) or player_id <= 0:
            raise ValueError("player_id must be a positive integer")

        cursor = self.conn.cursor()

        cursor.execute("""
                SELECT 
                    level_id, 
                    completed_at,
                    elapsed_time_seconds,
                    achieved_performance,
                    achieved_redundancy
                FROM player_completed_levels
                WHERE player_id = ?
                ORDER BY level_id DESC
            """, (player_id,))

        rows = cursor.fetchall()

        player_completed_levels = []
        for row in rows:
            player_completed_levels.append({"level_id": row[0],
                                            "completed_at": row[1],
                                            "elapsed_time_seconds": row[2],
                                            "achieved_performance": row[3],
                                            "achieved_redundancy": row[4]
                                            }
                                           )

        return player_completed_levels

    def get_level_completed_by_players(self, level_id: int) -> List[Dict[str, Any]]:
        """
        Retrieve all players who completed a specific level.

        Args:
            level_id: Level ID to query.

        Returns:
            List of dicts with player_id, completion_time, and scores.
            Empty list if no players completed this level.

        Raises:
            ValueError: If level_id is invalid.
        """
        if not isinstance(level_id, int) or level_id <= 0:
            raise ValueError("level_id must be a positive integer")

        cursor = self.conn.cursor()
        cursor.execute("""
                        SELECT 
                            player_id, 
                            completed_at,
                            elapsed_time_seconds,
                            achieved_performance,
                            achieved_redundancy
                        FROM player_completed_levels
                        WHERE level_id = ?
                        ORDER BY completed_at DESC
                    """, (level_id,))

        rows = cursor.fetchall()

        result = []
        for row in rows:
            result.append({"player_id": row[0],
                           "completed_at": row[1],
                           "elapsed_time_seconds": row[2],
                           "achieved_performance": row[3],
                           "achieved_redundancy": row[4]
                           }
                          )

        return result

    def get_unlocked_levels_by_player(self, player_id: int) -> List[Dict[str, Any]]:
        """
        Retrieve all unlocked levels for a specific player.

        Unlocking logic (sequential):
        - Level 1 is always unlocked
        - Level N is unlocked if Level N-1 is completed

        Args:
            player_id: ID of the player to query.

        Returns:
            List of dicts with level_id and difficulty for all unlocked levels.
            Each dict contains: {"level_id": int, "difficulty": str}

        Raises:
            ValueError: If player_id is invalid or not found in database.
        """
        # Validate player exists
        self.get_player_by_id(player_id)

        cursor = self.conn.cursor()
        # Fetch all completed levels for this player with difficulty via JOIN
        cursor.execute("""
                SELECT DISTINCT
                    pcl.level_id,
                    l.difficulty              
                FROM player_completed_levels pcl
                JOIN levels l ON pcl.level_id = l.id
                WHERE pcl.player_id = ?
                ORDER BY pcl.level_id ASC
            """, (player_id,))

        rows = cursor.fetchall()
        unlocked_levels = []

        # add all completed levels
        for row in rows:
            unlocked_levels.append({"level_id": row[0], "difficulty": row[1]})

        # find highest level_id
        if unlocked_levels:
            highest_level_id = unlocked_levels[-1]["level_id"]
        else:
            highest_level_id = 0

        try:
            next_level = self.get_level(highest_level_id + 1)
            unlocked_levels.append({
                "level_id": next_level.level_id,
                "difficulty": next_level.difficulty.display_name})
        except ValueError:
            # No more levels available - player has completed all levels
            pass

        return unlocked_levels

    def save_completed_level(self, player_id: int, level_id: int, elapsed_time_seconds: int,
                             achieved_redundancy: int, achieved_performance: int) -> None:
        """
        Save completed level attempt for player to database.

        Creates new entry for each completion, allowing multiple attempts
        per level to be tracked.

        Args:
            player_id: Player who completed the level.
            level_id: Level that was completed.
            elapsed_time_seconds: Time taken to complete level in seconds.
            achieved_performance: Performance score achieved.
            achieved_redundancy: Redundancy score achieved.

        Raises:
            ValueError: If player_id, level_id, or elapsed_time_seconds
                        is invalid or not found in database.
        """
        cursor = self.conn.cursor()

        # Validate inputs
        # Player_id
        cursor.execute("SELECT id, name FROM players WHERE id = ?", (player_id,))
        row = cursor.fetchone()
        if row is None:
            raise ValueError(f"Player ID {player_id} not found in database")
        # Level_id
        cursor.execute("SELECT id, difficulty FROM levels WHERE id = ?", (level_id,))
        row = cursor.fetchone()
        if row is None:
            raise ValueError(f"Level ID {level_id} not found in database")
        # elapsed_time
        if not isinstance(elapsed_time_seconds, int) or elapsed_time_seconds < 0:
            raise ValueError("elapsed_time_seconds must be non-negative integer")

        # Insert new attempt (allows multiple entries per player-level pair)
        cursor.execute("""
            INSERT INTO player_completed_levels (
                player_id,
                level_id,
                elapsed_time_seconds,
                achieved_performance,
                achieved_redundancy
            ) VALUES (?, ?, ?, ?, ?)
        """, (player_id, level_id, elapsed_time_seconds, achieved_performance, achieved_redundancy))

        self.conn.commit()
