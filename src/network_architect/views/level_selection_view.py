"""
Level selection view for choosing player and level to play.
"""

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QComboBox, QListWidget, QListWidgetItem,
                               QPushButton, QLabel, QMessageBox, QInputDialog)


class LevelSelectionView(QWidget):
    """View for selecting player and level before starting game."""

    # Signals
    start_game_clicked = Signal(int, int)  # player_id, level_id
    back_clicked = Signal()

    def __init__(self, viewmodel):
        """
        Initialize level selection view.

        Args:
            viewmodel: LevelSelectionViewModel instance
        """
        super().__init__()
        self.viewmodel = viewmodel

        # Track selection
        self.selected_player_id = None
        self.selected_level_id = None

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Title
        title_label = QLabel("Select Level")
        title_font = QFont("Arial", 24, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Player Selection Row
        player_layout = QHBoxLayout()

        player_label = QLabel("Player:")
        player_layout.addWidget(player_label)

        self.player_combo = QComboBox()
        self.player_combo.currentIndexChanged.connect(self._on_player_selected)
        player_layout.addWidget(self.player_combo)

        self.new_player_btn = QPushButton("+ New Player")
        self.new_player_btn.clicked.connect(self._on_new_player_clicked)
        player_layout.addWidget(self.new_player_btn)

        layout.addLayout(player_layout)

        # Level List
        levels_label = QLabel("Available Levels:")
        layout.addWidget(levels_label)

        self.levels_list = QListWidget()
        self.levels_list.itemClicked.connect(self._on_level_clicked)
        layout.addWidget(self.levels_list)

        # Buttons
        button_layout = QHBoxLayout()

        self.start_btn = QPushButton("Start Game")
        self.start_btn.setMinimumHeight(40)
        self.start_btn.setEnabled(False)  # Disabled until level selected
        self.start_btn.clicked.connect(self._on_start_game)
        button_layout.addWidget(self.start_btn)

        self.back_btn = QPushButton("Back to Menu")
        self.back_btn.setMinimumHeight(40)
        self.back_btn.clicked.connect(self.back_clicked.emit)
        button_layout.addWidget(self.back_btn)

        layout.addLayout(button_layout)

        # Connect ViewModel signals
        self.viewmodel.players_loaded.connect(self._update_player_dropdown)
        self.viewmodel.player_created.connect(self._on_player_created)
        self.viewmodel.unlocked_levels_loaded.connect(self._update_levels_list)
        self.viewmodel.error_occurred.connect(self._show_error)

        # Load initial data
        self.viewmodel.load_players_list()

    @Slot()
    def _update_player_dropdown(self):
        """Update player dropdown with available players."""
        self.player_combo.clear()

        if not self.viewmodel.players_list:
            self.player_combo.addItem("No players available", None)
            return

        for player in self.viewmodel.players_list:
            self.player_combo.addItem(player["name"], player["id"])

    @Slot(int)
    def _on_player_selected(self, index):
        """Load unlocked levels when player is selected."""

        if index >= 0:
            player_id = self.player_combo.itemData(index)

            if player_id is not None:
                self.selected_player_id = player_id
                self.viewmodel.load_unlocked_levels_list(player_id)
            else:
                self.levels_list.clear()
                self.selected_player_id = None

    @Slot()
    def _on_new_player_clicked(self):
        """Show dialog to create new player."""
        name, ok = QInputDialog.getText(
            self,
            "New Player",
            "Enter player name (2-20 characters):"
        )

        if ok:
            self.viewmodel.create_player(name.strip())

    @Slot()
    def _on_player_created(self):
        """Handle new player creation."""
        # Reload player list
        self.viewmodel.load_players_list()

        # Select the newly created player
        if self.viewmodel.new_player:
            new_player = self.viewmodel.new_player[0]
            index = self.player_combo.findData(new_player["id"])
            if index >= 0:
                self.player_combo.setCurrentIndex(index)

    @Slot()
    def _update_levels_list(self):
        """Update levels list with unlocked levels."""
        self.levels_list.clear()
        self.selected_level_id = None
        self.start_btn.setEnabled(False)

        for level_data in self.viewmodel.unlocked_levels_list:
            level_id = level_data["level_id"]
            difficulty = level_data["difficulty"]

            # Create list item
            item_text = f"Level {level_id} - {difficulty}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, level_id)

            self.levels_list.addItem(item)

    @Slot(QListWidgetItem)
    def _on_level_clicked(self, item):
        """Handle level selection."""
        self.selected_level_id = item.data(Qt.ItemDataRole.UserRole)
        self.start_btn.setEnabled(True)

    @Slot(int)
    def _on_player_selected(self, index):
        """Load unlocked levels when player is selected."""

        if index >= 0:
            player_id = self.player_combo.itemData(index)

            if player_id is not None:
                self.selected_player_id = player_id
                self.viewmodel.load_unlocked_levels_list(player_id)
            else:
                self.levels_list.clear()
                self.selected_player_id = None

    @Slot()
    def _on_start_game(self):
        """Validate and emit start game signal."""

        current_index = self.player_combo.currentIndex()
        player_id = self.player_combo.itemData(current_index)

        if player_id and self.selected_level_id:
            self.viewmodel.select_level_and_player(player_id, self.selected_level_id)
            self.start_game_clicked.emit(player_id, self.selected_level_id)
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Selection incomplete", "Please select both player and level.")

    @Slot(str)
    def _show_error(self, message):
        """Display error message to user."""
        QMessageBox.warning(self, "Error", message)
