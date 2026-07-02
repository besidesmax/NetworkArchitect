from enum import Enum


class Difficulty(Enum):
    """Difficulty level of a puzzle including its default board size."""

    LIGHT = ("LIGHT", 5, 9)
    MEDIUM = ("MEDIUM", 7, 9)
    HARD = ("HARD", 9, 11)

    def __init__(self, display_name: str, width: int, height: int) -> None:
        """Create a difficulty with an associated default board size.

        Args:
            display_name: Human‑readable name shown in the UI.
            width: Number of columns in the game grid.
            height: Number of rows in the game grid.
        """
        self.display_name = display_name
        self.width = width
        self.height = height
