"""
Level statistics tab showing players who completed each level.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QTableWidget, QTableWidgetItem, QLabel
from PySide6.QtCore import Qt, Slot


class LevelStatisticsTab(QWidget):
    """Tab for displaying level-specific statistics."""

    def __init__(self, viewmodel):
        """
        Initialize level statistics tab.

        Args:
            viewmodel: StatisticsViewModel instance
        """
        super().__init__()
        self.viewmodel = viewmodel

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Level Selection
        selection_label = QLabel("Select Level:")
        layout.addWidget(selection_label)

        self.level_combo = QComboBox()
        self.level_combo.currentIndexChanged.connect(self._on_level_selected)
        layout.addWidget(self.level_combo)

        # Results Table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["Player",
                                                      "Time (s)",
                                                      "Performance",
                                                      "Redundancy",
                                                      "Completed At"
                                                      ]
                                                     )
        layout.addWidget(self.results_table)

        # Connect Signals
        self.viewmodel.available_levels_changed.connect(self._update_level_dropdown)
        self.viewmodel.level_statistics_loaded.connect(self._update_results_table)

        # Load initial data
        self.viewmodel.load_available_levels()

    @Slot()
    def _update_level_dropdown(self):
        """Update level dropdown with available levels."""
        self.level_combo.clear()
        for level in self.viewmodel.available_levels:
            display_text = f"Level {level['id']} ({level['difficulty']})"
            self.level_combo.addItem(display_text, level["id"])

    @Slot(int)
    def _on_level_selected(self, index):
        """Load statistics when level is selected."""
        if index >= 0:
            level_id = self.level_combo.itemData(index)
            self.viewmodel.load_level_statistics(level_id)

    @Slot()
    def _update_results_table(self):
        """Update table with level statistics."""
        stats = self.viewmodel.level_statistics
        self.results_table.setRowCount(len(stats))

        for row, stat in enumerate(stats):
            self.results_table.setItem(row, 0, QTableWidgetItem(stat["player_name"]))
            self.results_table.setItem(row, 1, QTableWidgetItem(stat["elapsed_time_seconds"]))
            self.results_table.setItem(row, 2, QTableWidgetItem(str(stat["achieved_performance"])))
            self.results_table.setItem(row, 3, QTableWidgetItem(str(stat["achieved_redundancy"])))
            self.results_table.setItem(row, 2, QTableWidgetItem(stat["completed_at"]))
