import sys
import time
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QEventLoop

from models.database_service import DatabaseService
from views.splash_screen import SplashScreen
from views.main_window import MainWindow


def main():
    """Entry point for Network Architect application."""
    # 1. Create Qt application
    app = QApplication(sys.argv)

    # 2. Create and show splash screen
    splash = SplashScreen()
    splash.show()

    # 3. Force Qt to render splash immediately
    app.processEvents()

    # 4. Start measuring time
    start_time = time.time()

    # 5. Initialize database (splash is visible during this)
    db = DatabaseService()

    # 6. Calculate elapsed time
    elapsed_ms = (time.time() - start_time) * 1000  # Convert to milliseconds

    # 7. Calculate remaining time to reach minimum 3 seconds
    minimum_duration_ms = 3000
    remaining_ms = minimum_duration_ms - elapsed_ms

    # 8. Wait if needed (keeps UI responsive)
    if remaining_ms > 0:
        loop = QEventLoop()
        QTimer.singleShot(int(remaining_ms), loop.quit)
        loop.exec()

    # 9. Create and show main window
    main_window = MainWindow()
    main_window.show()

    # 10. Close splash screen
    splash.close()

    # 11. Start Qt event loop (app runs until user closes)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
