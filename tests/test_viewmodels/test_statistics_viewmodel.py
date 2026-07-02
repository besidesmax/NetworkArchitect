"""Unit tests for StatisticsViewModel."""

import pytest
from PySide6.QtCore import QObject

from network_architect.models.database_service import DatabaseService
from network_architect.models.difficulty import Difficulty
from network_architect.viewmodels.statistics_viewmodel import StatisticsViewModel


@pytest.fixture
def db_service(tmp_path):
    """Create temporary database for testing."""
    # Reset GridPoint counter for test isolation
    from network_architect.models.grid_point import GridPoint
    GridPoint.id_counter = 0
    GridPoint.all_instances = []

    db_path = str(tmp_path / "test.db")
    db = DatabaseService()
    db.db_path = db_path

    import sqlite3
    db.conn.close()
    db.conn = sqlite3.connect(db_path)
    db._init_schema()

    return db


@pytest.fixture
def sample_players(db_service):
    """Create sample players in database."""
    player1 = db_service.create_player("TestPlayer1")
    player2 = db_service.create_player("TestPlayer2")
    return [player1, player2]


@pytest.fixture
def sample_levels(db_service):
    """Create sample levels in database."""
    level1 = db_service.create_level(
        Difficulty.LIGHT,
        target_performance_score=80,
        target_redundancy_score=70,
        start_budget=100,
        node_config_json='[{"grid_point_id": 0, "node_type": "SERVER"}]'
    )

    level2 = db_service.create_level(
        Difficulty.MEDIUM,
        target_performance_score=85,
        target_redundancy_score=75,
        start_budget=120,
        node_config_json=f'[{{"grid_point_id": 0, "node_type": "SERVER"}}]'
    )
    return [level1, level2]


@pytest.fixture
def viewmodel(db_service):
    """Create StatisticsViewModel instance."""
    return StatisticsViewModel(db_service)


class TestStatisticsViewModelInit:
    """Test initialization of StatisticsViewModel."""

    def test_init_creates_instance(self, viewmodel):
        """Test that ViewModel initializes correctly."""
        assert isinstance(viewmodel, QObject)
        assert viewmodel._db_service is not None

    def test_init_initializes_backing_fields(self, viewmodel):
        """Test that all backing fields are initialized as empty lists."""
        assert viewmodel._player_statistics == []
        assert viewmodel._level_statistics == []
        assert viewmodel._available_players == []
        assert viewmodel._available_levels == []

    def test_signals_exist(self, viewmodel):
        """Test that all required signals are defined."""
        assert hasattr(viewmodel, 'available_players_changed')
        assert hasattr(viewmodel, 'available_levels_changed')
        assert hasattr(viewmodel, 'player_statistics_loaded')
        assert hasattr(viewmodel, 'level_statistics_loaded')


class TestLoadAvailablePlayers:
    """Test load_available_players slot."""

    def test_load_available_players_empty_db(self, viewmodel):
        """Test loading players when database is empty."""
        viewmodel.load_available_players()

        assert viewmodel.available_players == []

    def test_load_available_players_with_data(self, viewmodel, sample_players):
        """Test loading players from database."""
        viewmodel.load_available_players()

        assert len(viewmodel.available_players) == 2
        assert viewmodel.available_players[0]["name"] == "TestPlayer1"
        assert viewmodel.available_players[1]["name"] == "TestPlayer2"

    def test_load_available_players_returns_dicts(self, viewmodel, sample_players):
        """Test that players are converted to dicts with id and name."""
        viewmodel.load_available_players()

        player = viewmodel.available_players[0]
        assert "id" in player
        assert "name" in player
        assert isinstance(player["id"], int)
        assert isinstance(player["name"], str)

    def test_load_available_players_emits_signal(self, viewmodel, sample_players, qtbot):
        """Test that signal is emitted when players are loaded."""
        with qtbot.waitSignal(viewmodel.available_players_changed, timeout=1000):
            viewmodel.load_available_players()


class TestLoadAvailableLevels:
    """Test load_available_levels slot."""

    def test_load_available_levels_empty_db(self, viewmodel):
        """Test loading levels when database is empty."""
        viewmodel.load_available_levels()

        assert viewmodel.available_levels == []

    def test_load_available_levels_with_data(self, viewmodel, sample_levels):
        """Test loading levels from database."""
        viewmodel.load_available_levels()

        assert len(viewmodel.available_levels) == 2
        assert viewmodel.available_levels[0]["difficulty"] == "LIGHT"
        assert viewmodel.available_levels[1]["difficulty"] == "MEDIUM"

    def test_load_available_levels_returns_dicts(self, viewmodel, sample_levels):
        """Test that levels are converted to dicts with id and difficulty."""
        viewmodel.load_available_levels()

        level = viewmodel.available_levels[0]
        assert "id" in level
        assert "difficulty" in level
        assert isinstance(level["id"], int)
        assert isinstance(level["difficulty"], str)

    def test_load_available_levels_emits_signal(self, viewmodel, sample_levels, qtbot):
        """Test that signal is emitted when levels are loaded."""
        with qtbot.waitSignal(viewmodel.available_levels_changed, timeout=1000):
            viewmodel.load_available_levels()


class TestLoadPlayerStatistics:
    """Test load_player_statistics slot."""

    def test_load_player_statistics_no_completed_levels(self, viewmodel, sample_players):
        """Test loading statistics for player with no completed levels."""
        viewmodel.load_player_statistics(sample_players[0].player_id)

        assert viewmodel.player_statistics == []

    def test_load_player_statistics_with_completed_levels(self, viewmodel, db_service, sample_players, sample_levels):
        """Test loading statistics for player with completed levels."""
        # Add completed level to database
        cursor = db_service.conn.cursor()
        cursor.execute("""
            INSERT INTO player_completed_levels 
            (player_id, level_id, achieved_performance, achieved_redundancy)
            VALUES (?, ?, ?, ?)
        """, (sample_players[0].player_id, sample_levels[0].level_id, 85, 90))
        db_service.conn.commit()

        viewmodel.load_player_statistics(sample_players[0].player_id)

        assert len(viewmodel.player_statistics) == 1
        assert viewmodel.player_statistics[0]["level_id"] == sample_levels[0].level_id

    def test_load_player_statistics_emits_signal(self, viewmodel, sample_players, qtbot):
        """Test that signal is emitted when player statistics are loaded."""
        with qtbot.waitSignal(viewmodel.player_statistics_loaded, timeout=1000):
            viewmodel.load_player_statistics(sample_players[0].player_id)


class TestLoadLevelStatistics:
    """Test load_level_statistics slot."""

    def test_load_level_statistics_no_completed_players(self, viewmodel, sample_levels):
        """Test loading statistics for level with no completed players."""
        viewmodel.load_level_statistics(sample_levels[0].level_id)

        assert viewmodel.level_statistics == []

    def test_load_level_statistics_with_completed_players(self, viewmodel, db_service, sample_players, sample_levels):
        """Test loading statistics for level with completed players."""
        # Add completed level to database
        cursor = db_service.conn.cursor()
        cursor.execute("""
            INSERT INTO player_completed_levels 
            (player_id, level_id, achieved_performance, achieved_redundancy)
            VALUES (?, ?, ?, ?)
        """, (sample_players[0].player_id, sample_levels[0].level_id, 85, 90))
        db_service.conn.commit()

        viewmodel.load_level_statistics(sample_levels[0].level_id)

        assert len(viewmodel.level_statistics) == 1
        assert viewmodel.level_statistics[0]["player_id"] == sample_players[0].player_id

    def test_load_level_statistics_emits_signal(self, viewmodel, sample_levels, qtbot):
        """Test that signal is emitted when level statistics are loaded."""
        with qtbot.waitSignal(viewmodel.level_statistics_loaded, timeout=1000):
            viewmodel.load_level_statistics(sample_levels[0].level_id)


class TestProperties:
    """Test ViewModel properties."""

    def test_available_players_property(self, viewmodel):
        """Test that available_players property returns backing field."""
        test_data = [{"id": 1, "name": "Test"}]
        viewmodel._available_players = test_data

        assert viewmodel.available_players == test_data

    def test_available_levels_property(self, viewmodel):
        """Test that available_levels property returns backing field."""
        test_data = [{"id": 1, "difficulty": "Easy"}]
        viewmodel._available_levels = test_data

        assert viewmodel.available_levels == test_data

    def test_player_statistics_property(self, viewmodel):
        """Test that player_statistics property returns backing field."""
        test_data = [{"level_id": 1, "completed_at": "2024-01-01"}]
        viewmodel._player_statistics = test_data

        assert viewmodel.player_statistics == test_data

    def test_level_statistics_property(self, viewmodel):
        """Test that level_statistics property returns backing field."""
        test_data = [{"player_id": 1, "completed_at": "2024-01-01"}]
        viewmodel._level_statistics = test_data

        assert viewmodel.level_statistics == test_data
