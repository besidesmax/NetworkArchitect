from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class MainMenuView(QWidget):
    """Main menu view with navigation buttons."""
    # Signals für Navigation
    new_game_clicked = Signal()
    statistics_clicked = Signal()
    exit_clicked = Signal()

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        self.setLayout(layout)

        # Title
        title_label = QLabel("Network Architect")
        title_font = QFont("Arial", 32, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Buttons
        self.new_game_btn = QPushButton("New Game")
        self.new_game_btn.setMinimumHeight(50)
        self.new_game_btn.clicked.connect(self.new_game_clicked.emit)
        layout.addWidget(self.new_game_btn)

        self.statistics_btn = QPushButton("Statistic")
        self.statistics_btn.setMinimumHeight(50)
        self.statistics_btn.clicked.connect(self.statistics_clicked.emit)
        layout.addWidget(self.statistics_btn)

        self.exit_btn = QPushButton("Exit")
        self.exit_btn.setMinimumHeight(50)
        self.exit_btn.clicked.connect(self.exit_clicked.emit)
        layout.addWidget(self.exit_btn)
