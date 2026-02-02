from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QStackedWidget
from PySide6.QtGui import QIcon
from .statistics_view import StatisticsView


class MainWindow(QMainWindow):
    """Initialize main window and setup view navigation."""

    def __init__(self, db_service):
        """
        Initialize main window and setup view navigation.

        Args:
            db_service: DatabaseService instance for ViewModels
        """
        super().__init__()

        self.db_service = db_service
        self.setWindowTitle("Network Architect")
        self.setMinimumSize(800, 600)
        icon = QIcon("src/resources/logo.png")
        self.setWindowIcon(icon)

        # Stacked Widget for changing view
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Import and create views
        from views.main_menu_view import MainMenuView
        self.main_menu_view = MainMenuView()
        self.stack.addWidget(self.main_menu_view)

        # Connect signals
        self.main_menu_view.new_game_clicked.connect(self.show_level_selection_view)
        self.main_menu_view.statistics_clicked.connect(self.show_statistics_view)
        self.main_menu_view.exit_clicked.connect(self.close)

        # Statistics view
        self.statistics_view = None

        # Statistics view
        self.level_selection_view = None

        # Game view
        self.game_view = None

    def show_level_selection_view(self):
        """Display the level selection view."""

        if self.level_selection_view is None:
            from viewmodels.level_selection_viewmodel import LevelSelectionViewModel
            from views.level_selection_view import LevelSelectionView

            level_selection_viewmodel = LevelSelectionViewModel(self.db_service)
            self.level_selection_view = LevelSelectionView(level_selection_viewmodel)

            self.level_selection_view.back_clicked.connect(self.show_main_menu)
            self.level_selection_view.start_game_clicked.connect(self.show_game_view)

            self.stack.addWidget(self.level_selection_view)

        self.stack.setCurrentWidget(self.level_selection_view)

    def show_main_menu(self):
        """Return to main menu."""
        self.stack.setCurrentWidget(self.main_menu_view)

    def show_statistics_view(self):
        """Display the statistics view."""
        if self.statistics_view is None:
            from viewmodels.statistics_viewmodel import StatisticsViewModel
            from views.statistics_view import StatisticsView

            stats_viewmodel = StatisticsViewModel(self.db_service)
            self.statistics_view = StatisticsView(stats_viewmodel)

            self.statistics_view.back_clicked.connect(self.show_main_menu)

            self.stack.addWidget(self.statistics_view)

        self.stack.setCurrentWidget(self.statistics_view)

    def show_game_view(self, player_id: int, level_id: int):
        """Display game view with selected player and level."""
        from viewmodels.game_viewmodel import GameViewModel
        from views.game_view import GameView

        game_vm = GameViewModel(player_id, level_id, self.db_service)

        game_view = GameView(game_vm)

        game_view.navigate_to_main_menu.connect(self.show_main_menu)
        game_view.navigate_to_level_selection.connect(self.show_level_selection_view)

        if self.game_view is not None:
            self.stack.removeWidget(self.game_view)
            self.game_view.deleteLater()

        self.game_view = game_view

        self.stack.addWidget(game_view)
        self.stack.setCurrentWidget(game_view)
