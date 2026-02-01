"""
Player statistics tab showing completed levels per player.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QTableWidget, QTableWidgetItem, QLabel
from PySide6.QtCore import Qt, Slot


class PlayerStatisticsTab(QWidget):
    """Tab for displaying player-specific statistics."""

    def __init__(self, viewmodel):
        """
        Initialize player statistics tab.

        Args:
            viewmodel: StatisticsViewModel instance
        """
        super().__init__()
        self.viewmodel = viewmodel

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Player Selection
        selection_label = QLabel("Select Player:")
        layout.addWidget(selection_label)

        self.player_combo = QComboBox()
        self.player_combo.currentIndexChanged.connect(self._on_player_selected)
        layout.addWidget(self.player_combo)

        # Results Table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels(["Level ID",
                                                      "Difficulty",
                                                      "Time (s)",
                                                      "Performance",
                                                      "Redundancy",
                                                      "Completed At"
                                                      ]
                                                     )
        layout.addWidget(self.results_table)

        # Connect Signals
        self.viewmodel.available_players_changed.connect(self._update_player_dropdown)
        self.viewmodel.player_statistics_loaded.connect(self._update_results_table)

        # Load initial data
        self.viewmodel.load_available_players()

    @Slot()
    def _update_player_dropdown(self):
        """Update player dropdown with available players."""
        self.player_combo.clear()
        for player in self.viewmodel.available_players:
            self.player_combo.addItem(player["name"], player["id"])

    @Slot(int)
    def _on_player_selected(self, index):
        """Load statistics when player is selected."""
        if index >= 0:
            player_id = self.player_combo.itemData(index)
            self.viewmodel.load_player_statistics(player_id)

    @Slot()
    def _update_results_table(self):
        """Update table with player statistics."""
        stats = self.viewmodel.player_statistics
        self.results_table.setRowCount(len(stats))

        for row, stat in enumerate(stats):
            self.results_table.setItem(row, 0, QTableWidgetItem(str(stat["level_id"])))
            self.results_table.setItem(row, 1, QTableWidgetItem(stat["difficulty"]))
            self.results_table.setItem(row, 2, QTableWidgetItem(str(stat["elapsed_time_seconds"])))
            self.results_table.setItem(row, 3, QTableWidgetItem(str(stat["achieved_performance"])))
            self.results_table.setItem(row, 4, QTableWidgetItem(str(stat["achieved_redundancy"])))
            self.results_table.setItem(row, 5, QTableWidgetItem(stat["completed_at"]))
