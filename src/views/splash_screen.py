from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from config import Config


class SplashScreen(QWidget):
    """Splash screen displayed during application initialization."""

    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )

        self.setFixedSize(400, 300)

        # set layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        #  Create widgets
        logo_label = QLabel()
        logo_pixmap = QPixmap(str(Config.ICON_PATH))
        if logo_pixmap.isNull():
            print("⚠️ Logo not found!")
        logo_pixmap = logo_pixmap.scaled(
            90, 90,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel("Network Architect")
        title_font = QFont("Arial", 24, QFont.Weight.Bold)
        title_label.setFont(title_font)

        version_label = QLabel("Version 1.0")
        version_font = QFont("Arial", 10)
        version_label.setFont(version_font)

        loading_label = QLabel("Initializing...")
        loading_font = QFont("Arial", 10)
        loading_label.setFont(loading_font)

        # Add widgets to layout
        layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(loading_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Apply styling
        self.setStyleSheet("""  QWidget {background-color: #1e1e1e;}
                                QLabel {color: #ffffff;}""")

        logo_label.setStyleSheet("""
            background-color: #2c3e50;
            border-radius: 10px;
            border: 2px solid #3498db;""")

        title_label.setStyleSheet("color: #3498db;")

        # Center window on screen
        self._center_on_screen()

    def _center_on_screen(self):
        """Center the splash screen on the primary screen."""
        screen = QApplication.primaryScreen().geometry()
        window_geometry = self.frameGeometry()

        # Calculate center position
        center_x = (screen.width() - window_geometry.width()) // 2
        center_y = (screen.height() - window_geometry.height()) // 2

        # Move window to center
        self.move(center_x, center_y)
