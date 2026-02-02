from PySide6.QtCore import Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene


class GameCanvas(QGraphicsView):
    canvas_clicked = Signal(object)

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
        self.canvas_clicked.emit(scene_pos)
        super().mousePressEvent(event)
