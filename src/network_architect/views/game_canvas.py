from PySide6.QtCore import Signal
from PySide6.QtGui import QMouseEvent, Qt
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene


class GameCanvas(QGraphicsView):
    canvas_clicked_left = Signal(object)
    canvas_clicked_right = Signal()

    def __init__(self, scene: QGraphicsScene):
        """
        Initialize the game canvas with a graphics scene.

        Args:
            scene: QGraphicsScene containing the game board elements
        """
        super().__init__(scene)

    def mousePressEvent(self, event: QMouseEvent):
        """
        Handle mouse press events and emit click position in scene coordinates.

        Args:
            event: Mouse event containing click information
        """
        scene_pos = self.mapToScene(event.pos())

        if event.button() == Qt.MouseButton.LeftButton:
            self.canvas_clicked_left.emit(scene_pos)

        if event.button() == Qt.MouseButton.RightButton:
            self.canvas_clicked_right.emit()

        super().mousePressEvent(event)
