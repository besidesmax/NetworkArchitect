"""
Statistics view with tabs for player and level statistics.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QPushButton, QLabel


class StatisticsView(QWidget):
    """Statistics view with tabs for different statistic types."""

    # Signal for navigation
    back_clicked = Signal()

    def __init__(self, viewmodel):
        """
        Initialize statistics view with tabs.

        Args:
            viewmodel: StatisticsViewModel instance
        """
        super().__init__()
        self.viewmodel = viewmodel

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

        # Title
        title_label = QLabel("Statistics")
        title_font = QFont("Arial", 24, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Tab Widget
        self.tab_widget = QTabWidget()

        # Import Tab-Widgets
        from network_architect.views.player_statistics_tab import PlayerStatisticsTab
        from network_architect.views.level_statistics_tab import LevelStatisticsTab

        self.player_tab = PlayerStatisticsTab(self.viewmodel)
        self.level_tab = LevelStatisticsTab(self.viewmodel)

        self.tab_widget.addTab(self.player_tab, "Player Statistics")
        self.tab_widget.addTab(self.level_tab, "Level Statistics")

        layout.addWidget(self.tab_widget)

        # Back Button
        self.back_btn = QPushButton("Back to Menu")
        self.back_btn.setMinimumHeight(40)
        self.back_btn.clicked.connect(self.back_clicked.emit)
        layout.addWidget(self.back_btn)
