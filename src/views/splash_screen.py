from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap


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
        logo_label.setFixedSize(100, 100)  # Reserve space for logo # TODO insert Logo
        logo_label.setStyleSheet("background-color: #2c3e50; border-radius: 10px;")

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
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #ffffff;
            }
        """)

        # Update logo placeholder style for better contrast
        logo_label.setStyleSheet("""
            background-color: #2c3e50;
            border-radius: 10px;
            border: 2px solid #3498db;
        """)

        # Optional: Add color to title
        title_label.setStyleSheet("color: #3498db;")  # Blue title


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    sys.exit(app.exec())
