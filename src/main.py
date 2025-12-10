import sys
from PySide6.QtWidgets import QApplication, QMainWindow


class MainWindow(QMainWindow):
    """Main window for the Network Architect."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Network Architect")
        # TODO: inject ViewModel and set central widget later


def main() -> None:
    """Application entry point."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
