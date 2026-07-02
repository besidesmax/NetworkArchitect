import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from network_architect.models.database_service import DatabaseService
from network_architect.views.splash_screen import SplashScreen
from network_architect.views.main_window import MainWindow


def main():
    """Entry point for Network Architect application."""
    app = QApplication(sys.argv)

    # Initialize DatabaseService
    db_service = DatabaseService()

    # Show splash screen
    splash = SplashScreen()
    splash.show()

    # Create main window (but don't show yet)
    main_window = MainWindow(db_service)

    # Close splash and show main window after delay
    def show_main_window():
        splash.close()
        main_window.show()

    QTimer.singleShot(2000, show_main_window)  # 2 seconds

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
