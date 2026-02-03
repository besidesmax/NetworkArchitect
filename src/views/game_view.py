"""
Main game view for playing Network Architect puzzles.
"""

from PySide6.QtCore import Qt, Signal, Slot, QPointF, QRectF
from PySide6.QtGui import QFont, QPen, QBrush, QColor, QPainter
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
                               QMessageBox, QGraphicsScene,
                               QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem,
                               QScrollArea, QGraphicsItem)

from viewmodels.coordinate_mapper import CoordinateMapper
from .game_canvas import GameCanvas


class GameView(QWidget):
    """Main game view with 3-panel layout."""

    # Signals for navigation
    navigate_to_main_menu = Signal()
    navigate_to_level_selection = Signal()

    def __init__(self, viewmodel):
        """
        Initialize game view.

        Args:
            viewmodel: GameViewModel instance
        """
        super().__init__()
        self.viewmodel = viewmodel

        # Coordinate Mapper for grid-to-screen transformation
        self.coord_mapper = CoordinateMapper()

        # Graphics Scene for game board
        self.scene = QGraphicsScene()

        # Bridge placement state
        self.placement_active = False
        self.placement_from_node_id = None
        self.placement_grid_points = []  # List of grid_point_ids

        # Main Layout (Horizontal 3-Panel)
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Create panels
        self._create_left_panel(main_layout)
        self._create_center_panel(main_layout)
        self._create_right_panel(main_layout)

        # Connect ViewModel signals
        self._connect_viewmodel_signals()

        # Initial rendering
        self._render_game_board()
        self._render_nodes()
        self._render_bridges()

        # === PANEL CREATION ===
        self._update_budget_label(self.viewmodel.current_budget)

        # === Bridge Placement ===
        self._selected_from_node_item: QGraphicsItem | None = None
        self._selected_to_node_item: QGraphicsItem | None = None
        self._selected_grid_points_item: list[QGraphicsItem] = []

        # === debug ===
        # self._print_all_node_ids()

    def _create_left_panel(self, parent_layout):
        """Create left sidebar with control buttons."""
        left_panel = QVBoxLayout()
        left_panel.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Title
        title_label = QLabel("Controls")
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        title_label.setFont(title_font)
        left_panel.addWidget(title_label)

        # Main Menu Button
        self.main_menu_btn = QPushButton("Hauptmenü")
        self.main_menu_btn.setMinimumHeight(40)
        self.main_menu_btn.clicked.connect(self.viewmodel.request_navigate_to_main_menu)
        left_panel.addWidget(self.main_menu_btn)

        # Level Selection Button
        self.level_select_btn = QPushButton("Levelauswahl")
        self.level_select_btn.setMinimumHeight(40)
        self.level_select_btn.clicked.connect(self.viewmodel.request_navigate_to_level_selection)
        left_panel.addWidget(self.level_select_btn)

        # Reset Button
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setMinimumHeight(40)
        self.reset_btn.clicked.connect(self.viewmodel.reset_level)
        left_panel.addWidget(self.reset_btn)

        # Timer Label
        self.time_label = QLabel("Zeit: 00:00")
        time_font = QFont("Arial", 12)
        self.time_label.setFont(time_font)
        left_panel.addWidget(self.time_label)

        # Validate Button
        self.validate_btn = QPushButton("Lösung prüfen")
        self.validate_btn.setMinimumHeight(40)
        self.validate_btn.clicked.connect(self.viewmodel.validate_solution)
        left_panel.addWidget(self.validate_btn)

        left_panel.addStretch()
        parent_layout.addLayout(left_panel, 1)

    def _create_center_panel(self, parent_layout):
        """Create center game canvas (QGraphicsView)."""
        self.game_canvas = GameCanvas(self.scene)
        self.game_canvas.setMinimumSize(500, 500)
        self.game_canvas.setRenderHint(QPainter.RenderHint.Antialiasing)

        parent_layout.addWidget(self.game_canvas, 3)

    def _create_right_panel(self, parent_layout):
        """Create right sidebar with budget and bridge types."""
        right_panel = QVBoxLayout()
        right_panel.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Budget Label
        self.budget_label = QLabel("Budget: 0€")
        budget_font = QFont("Arial", 14, QFont.Weight.Bold)
        self.budget_label.setFont(budget_font)
        right_panel.addWidget(self.budget_label)

        # Bridge Types Label
        bridge_title = QLabel("Bridge Types:")
        title_font = QFont("Arial", 12, QFont.Weight.Bold)
        bridge_title.setFont(title_font)
        right_panel.addWidget(bridge_title)

        # Bridge Type Selection (ScrollArea with buttons)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        bridge_layout = QVBoxLayout(scroll_content)

        # Create bridge type buttons
        self.bridge_type_buttons = {}
        for bt in self.viewmodel.available_bridge_types:
            btn = QPushButton(f"{bt['name']}\n{bt['bandwidth']} Mbps\n{bt['cost']}€")
            btn.setMinimumHeight(60)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, name=bt['name']: self._on_bridge_type_selected(name))
            bridge_layout.addWidget(btn)
            self.bridge_type_buttons[bt['name']] = btn

        # Create bridge place button
        place_btn = QPushButton("Brücke platzieren")
        place_btn.setMinimumHeight(60)
        place_btn.setCheckable(True)
        place_btn.clicked.connect(self._on_bridge_place_clicked)
        self.bridge_place_btn = place_btn

        # add Widget zo right panel
        bridge_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        right_panel.addWidget(scroll_area)
        right_panel.addWidget(place_btn)

        parent_layout.addLayout(right_panel, 1)

    # === RENDERING METHODS ===

    def _grid_to_screen(self, grid_x, grid_y):
        """
        Helper: Convert grid coordinates to screen pixels.

        Args:
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate

        Returns:
            Tuple of (screen_x, screen_y)
        """
        x = grid_x * self.coord_mapper.cell_size + self.coord_mapper.offset_x
        y = grid_y * self.coord_mapper.cell_size + self.coord_mapper.offset_y
        return x, y

    def _render_game_board(self):
        """Render all grid points as small gray circles."""
        grid_points = self.viewmodel.game_board

        # Store node graphics for later updates
        self.grid_points_graphics = {}

        for gp_data in grid_points:
            x, y = self._grid_to_screen(gp_data["x"], gp_data["y"])
            grid_point_id = gp_data["id"]
            grid_point_x = gp_data["x"]
            grid_point_y = gp_data["y"]

            # Draw small circle
            circle = QGraphicsEllipseItem(x - 2, y - 2, 6, 6)
            circle.setBrush(QBrush(QColor(200, 200, 200)))
            circle.setPen(QPen(QColor(50, 50, 50), 1))
            circle.setData(0, grid_point_id)  # Store grid_point_id
            circle.setData(1, "grid_point")  # Store type
            circle.setData(2, grid_point_x)  # Store grid_point_x
            circle.setData(3, grid_point_y)  # Store grid_point_y
            self.scene.addItem(circle)

            # Store references for updates
            self.grid_points_graphics[grid_point_id] = {"circle": circle}

    def _render_nodes(self):
        """Render all nodes with their type and connection count."""
        nodes = self.viewmodel.nodes

        # Store node graphics for later updates
        self.node_graphics = {}

        for node in nodes:
            x, y = self._grid_to_screen(node["x"], node["y"])
            node_type = node["type"]
            node_id = node["id"]
            node_x = node["x"]
            node_y = node["y"]

            # Node colors by type
            color_map = {"SERVER": QColor(100, 150, 255),  # Blue
                         "CLIENT": QColor(100, 255, 150),  # Green
                         "ROUTER": QColor(255, 200, 100),  # Orange
                         "FIREWALL": QColor(255, 100, 100),  # Red
                         }

            color = color_map.get(node_type, QColor(128, 128, 128))

            # Draw node circle
            node_circle = QGraphicsEllipseItem(x - 15, y - 15, 30, 30)
            node_circle.setBrush(QBrush(color))
            node_circle.setPen(QPen(Qt.GlobalColor.black, 2))
            node_circle.setData(0, node_id)  # Store node_id
            node_circle.setData(1, "node")  # Store Type
            node_circle.setData(2, node_x)  # Store x-coordinate
            node_circle.setData(3, node_y)  # Store y-coordinate
            self.scene.addItem(node_circle)

            # Draw node label (type abbreviation)
            label_map = {"SERVER": "S",
                         "CLIENT": "C",
                         "ROUTER": "R",
                         "FIREWALL": "F",
                         }
            label_text = label_map.get(node_type, "?")

            label = QGraphicsTextItem(label_text)
            label.setPos(x - 8, y - 10)
            label.setDefaultTextColor(Qt.GlobalColor.white)
            font = QFont("Arial", 10, QFont.Weight.Bold)
            label.setFont(font)
            self.scene.addItem(label)

            # Draw connection count
            conn_text = f"{node['current_connections']}/{node['max_connections']}"
            conn_label = QGraphicsTextItem(conn_text)
            conn_label.setPos(x - 10, y + 15)
            font_small = QFont("Arial", 8)
            conn_label.setFont(font_small)
            self.scene.addItem(conn_label)

            # Store references for updates
            self.node_graphics[node_id] = {"circle": node_circle,
                                           "label": label,
                                           "conn_label": conn_label
                                           }

    def _render_bridges(self):
        """Render all bridges as colored lines."""
        bridges = self.viewmodel.bridges

        # Clear old bridges
        if hasattr(self, 'bridge_graphics'):
            for bridge_items in self.bridge_graphics.values():
                for item in bridge_items:
                    self.scene.removeItem(item)

        self.bridge_graphics = {}

        for bridge in bridges:
            bridge_id = bridge["bridge_id"]
            bridge_type = bridge["bridge_type"]
            grid_points = bridge["grid_points"]

            # Bridge colors and styles by type
            style_map = {
                "FIBER": {"color": QColor(0, 100, 255), "width": 4},
                "ETHERNET": {"color": QColor(0, 200, 100), "width": 3},
                "WLAN": {"color": QColor(255, 150, 0), "width": 2}
            }

            style = style_map.get(bridge_type, {"color": QColor(128, 128, 128), "width": 2})

            pen = QPen(style["color"], style["width"])
            if bridge_type == "WLAN":
                pen.setStyle(Qt.PenStyle.DashLine)

            # Draw lines between grid points
            bridge_items = []
            for i in range(len(grid_points) - 1):
                x1, y1 = self._grid_to_screen(
                    grid_points[i]["grid_point_x"],
                    grid_points[i]["grid_point_y"]
                )
                x2, y2 = self._grid_to_screen(
                    grid_points[i + 1]["grid_point_x"],
                    grid_points[i + 1]["grid_point_y"]
                )

                line = QGraphicsLineItem(x1, y1, x2, y2)
                line.setPen(pen)
                line.setData(0, bridge_id)  # Store bridge_id for removal
                line.setData(1, "bridge")
                self.scene.addItem(line)
                bridge_items.append(line)

            self.bridge_graphics[bridge_id] = bridge_items

    # === SLOTS ===
    @Slot(str)
    def _update_time_label(self, time_str):
        """Update timer display."""
        self.time_label.setText(f"Zeit: {time_str}")

    @Slot(int)
    def _update_budget_label(self, budget):
        """Update budget display."""
        self.budget_label.setText(f"Budget: {budget}€")

    @Slot()
    def _on_nodes_changed(self):
        """Update node connection counts when nodes change."""
        nodes = self.viewmodel.nodes

        for node in nodes:
            node_id = node["id"]
            if node_id in self.node_graphics:
                conn_text = f"{node['current_connections']}/{node['max_connections']}"
                self.node_graphics[node_id]["conn_label"].setPlainText(conn_text)

    @Slot()
    def _on_bridges_changed(self):
        """Re-render bridges when they change."""
        self._render_bridges()

    @Slot()
    def _on_game_reset(self):
        """Re-render everything on game reset."""
        self.scene.clear()
        self._render_game_board()
        self._render_nodes()
        self._render_bridges()

    @Slot(str)
    def _on_confirm_navigation(self, target):
        """Show confirmation dialog for navigation."""
        reply = QMessageBox.question(
            self,
            "Level verlassen?",
            "Fortschritt geht verloren. Wirklich verlassen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )

        if reply == QMessageBox.StandardButton.Yes:
            if target == "main_menu":
                self.navigate_to_main_menu.emit()
            elif target == "level_selection":
                self.navigate_to_level_selection.emit()
        else:
            # User canceled - resume timer
            self.viewmodel.resume_timer()

    @Slot(str)
    def _show_error(self, message):
        """Display error message."""
        QMessageBox.warning(self, "Fehler", message)

    @Slot(int, int, str)
    def _on_level_completed(self, redundancy, performance, time):
        """Show level completion dialog."""
        QMessageBox.information(
            self,
            "Level geschafft!",
            f"Zeit: {time}\nPerformance: {performance}\nRedundanz: {redundancy}"
        )

    @Slot(str)
    def _on_bridge_type_selected(self, bridge_type_name):
        """Handle bridge type button click."""
        # Uncheck all other buttons
        for name, btn in self.bridge_type_buttons.items():
            if name != bridge_type_name:
                btn.setChecked(False)

        # Set selected bridge type in ViewModel
        self.viewmodel.set_selected_bridge_type(bridge_type_name)

    @Slot()
    def _on_bridge_place_clicked(self):
        from_node = self._selected_from_node_item
        to_node = self._selected_to_node_item
        grid_points = self._selected_grid_points_item
        if from_node is None or to_node is None:
            print("from or to node not selected")
            self.bridge_place_btn.setChecked(False)
            return

        if grid_points:
            print(f"From Node ID = {from_node.data(0)}")
            print(f"To Node ID = {to_node.data(0)}")
            for gp in grid_points:
                print(f"Gridpoint_ID = {gp.data(0)} selected")
            self.bridge_place_btn.setChecked(False)
            return

        if not grid_points:
            print(f"From Node ID = {from_node.data(0)}")
            print(f"To Node ID = {to_node.data(0)}")
            self.bridge_place_btn.setChecked(False)
            return

    @Slot(QPointF)
    def _on_canvas_clicked(self, coordinates: QPointF):
        if self.viewmodel.selected_bridge_type == "":
            QMessageBox.warning(self, "Fehler", "BridgeType muss selected sein")

        else:
            x_coordinate = coordinates.x()
            y_coordinate = coordinates.y()
            radius = 5  # radius for rect

            rect = QRectF(x_coordinate - radius, y_coordinate - radius, radius * 2, radius * 2)

            items = self.scene.items(rect)
            items_data_1 = []
            for item in items:
                items_data_1.append(item.data(1))
            if "node" not in items_data_1 and self._selected_from_node_item is None:
                QMessageBox.warning(self, "Fehler", "Kein Node ausgewählt")
                return

            if "node" not in items_data_1 and "grid_point" not in items_data_1:
                QMessageBox.warning(self, "Fehler", "Kein Node oder GridPoint ausgewählt")
                return

            else:

                for item in items:
                    if item.data(1) == "node":
                        if self._selected_from_node_item is None:
                            self._selected_from_node_item = item
                            circle = self.node_graphics[item.data(0)]["circle"]
                            circle.setPen(QPen(QColor(255, 255, 0), 4))
                            break
                        if self._selected_from_node_item.data(0) == item.data(0):
                            circle = self.node_graphics[item.data(0)]["circle"]
                            circle.setPen(QPen(Qt.GlobalColor.black, 2))
                            self._selected_from_node_item = None
                            break
                        if self._selected_to_node_item is None:
                            self._selected_to_node_item = item
                            circle = self.node_graphics[item.data(0)]["circle"]
                            circle.setPen(QPen(QColor(255, 200, 0), 4))
                            break
                        if self._selected_to_node_item.data(0) == item.data(0):
                            circle = self.node_graphics[item.data(0)]["circle"]
                            circle.setPen(QPen(Qt.GlobalColor.black, 2))
                            self._selected_to_node_item = None
                            break
                        else:
                            QMessageBox.warning(self,
                                                "Fehler",
                                                "bereits ein from_node und ein to_node gewählt"
                                                "\n(abwählen = erneut auswählen)"
                                                )
                            break

                    if item.data(1) == "grid_point":
                        count = len(self._selected_grid_points_item)
                        if not self._selected_grid_points_item:
                            point1 = self._selected_from_node_item
                            point2 = item
                            if self.are_points_adjacent(point1, point2)[0] is True:
                                circle = self.grid_points_graphics[item.data(0)]["circle"]
                                circle.setPen(QPen(QColor(65, 105, 225), 4))
                                self._selected_grid_points_item.append(item)
                                break
                            if self.are_points_adjacent(point1, point2)[0] is False:
                                text = self.are_points_adjacent(point1, point2)[1]
                                QMessageBox.warning(self, "Fehler", text)
                                break

                        if self._selected_grid_points_item:
                            point1 = self._selected_grid_points_item[count - 1]
                            point2 = item
                            if item in self._selected_grid_points_item:
                                if item == self._selected_grid_points_item[count - 1]:
                                    circle = self.grid_points_graphics[item.data(0)]["circle"]
                                    circle.setPen(QPen(QColor(50, 50, 50), 1))
                                    self._selected_grid_points_item.remove(item)
                                    break
                                if not item == self._selected_grid_points_item[count - 1]:
                                    QMessageBox.warning(self, "Fehler", "wurde bereits hinzugefügt und nur"
                                                                        " der als  letztes hinzugefügte GriPoint"
                                                                        " kann entfernt werden")
                                    break
                            if self.are_points_adjacent(point1, point2)[0] is True:
                                circle = self.grid_points_graphics[item.data(0)]["circle"]
                                circle.setPen(QPen(QColor(65, 105, 225), 4))
                                self._selected_grid_points_item.append(item)
                                break
                            if self.are_points_adjacent(point1, point2)[0] is False:
                                text = self.are_points_adjacent(point1, point2)[1]
                                QMessageBox.warning(self, "Fehler", text)
                                break

    # === Methods ===
    def _connect_viewmodel_signals(self):
        """Connect all ViewModel signals to View slots."""
        self.viewmodel.time_updated.connect(self._update_time_label)
        self.viewmodel.budget_changed.connect(self._update_budget_label)
        self.viewmodel.confirm_navigation.connect(self._on_confirm_navigation)
        self.viewmodel.error_occurred.connect(self._show_error)
        self.viewmodel.level_completed.connect(self._on_level_completed)
        self.viewmodel.game_reset.connect(self._on_game_reset)
        self.viewmodel.nodes_changed.connect(self._on_nodes_changed)
        self.viewmodel.bridges_changed.connect(self._on_bridges_changed)
        self.game_canvas.canvas_clicked.connect(self._on_canvas_clicked)

    @staticmethod
    def are_points_adjacent(point_1: QGraphicsItem, point_2: QGraphicsItem) -> tuple[bool, str]:
        """
        Check if two QGraphicsItems are horizontally or vertically adjacent.

        Points are considered adjacent if they differ by exactly 1 in either
        the x-coordinate OR y-coordinate (but not both - no diagonal).

        Args:
            point_1: First graphics item with x/y coordinates stored in data(2) and data(3)
            point_2: Second graphics item with x/y coordinates stored in data(2) and data(3)

        Returns:
            tuple[bool, str]: (is_adjacent, error_message)
                - (True, "") if points are adjacent
                - (False, "reason") if points are not adjacent or diagonal
        """
        point1_x = point_1.data(2)
        point1_y = point_1.data(3)
        point2_x = point_2.data(2)
        point2_y = point_2.data(3)

        # Test x coordinate
        if not (point1_x == point2_x
                or point1_x == point2_x + 1
                or point1_x == point2_x - 1):
            return False, (f"X-Position: Point1 (Type: {point_1.data(1)} | ID = {point_1.data(0)})"
                           f"liegt nicht neben Point2 (Type: {point_2.data(1)} | ID = {point_2.data(0)})")

        # Test y coordinate
        if not (point1_y == point2_y
                or point1_y == point2_y + 1
                or point1_y == point2_y - 1):
            return False, (f"Y-Position: Point1 (Type: {point_1.data(1)} | ID = {point_1.data(0)})"
                           f"liegt nicht neben Point2 (Type: {point_2.data(1)} | ID = {point_2.data(0)})")

        # test if Points are diagonal to each other
        if ((point1_x == point2_x + 1 or
             point1_x == point2_x - 1)
                and
                (point1_y == point2_y + 1 or
                 point1_y == point2_y - 1)):
            return False, (f"Diagonal: Point1 (Type: {point_1.data(1)} | ID = {point_1.data(0)})"
                           f"ist nicht diagonal zu Point2 (Type: {point_2.data(1)} | ID = {point_2.data(0)})")

        return True, ""

# ===== TEST ====== TEST ====
#     def _print_all_node_ids(self):
#         """
#         Debug method: Print all node_ids from ViewModel.
#         """
#         print(self.node_graphics)
#
