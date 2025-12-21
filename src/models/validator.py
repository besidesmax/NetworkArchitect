from models.grid_point import GridPoint
from models.node import Node


class Validator:
    """this class validates all game rules"""
    @staticmethod
    def is_grid_point_used(grid_points: list[GridPoint]) -> None:
        """Check if any GridPoint is already used and mark them used."""
        for points in grid_points:
            if points.used:
                raise ValueError("GridPoint", {points.grid_point_id}, "is already used")
            points.used = True

    @staticmethod
    def is_first_grid_point_adjacent(from_node: Node, grid_points: list[GridPoint]) -> None:
        """Check if  1.GridPoint is adjacent to from_node."""
        # test if the 1. grid_point is next to from_node
        from_node_x = from_node.grid_point[0].position_x
        if not (
                grid_points[0].position_x == from_node_x
                or grid_points[0].position_x == from_node_x + 1
                or grid_points[0].position_x == from_node_x - 1
        ):
            raise ValueError("X-Position: from_node is not next to first grid_point")

        from_node_y = from_node.grid_point[0].position_y
        if not (
                grid_points[0].position_y == from_node_y
                or grid_points[0].position_y == from_node_y + 1
                or grid_points[0].position_y == from_node_y - 1
        ):
            raise ValueError("Y-Position: from_node is not next to first grid_point")

        # test if the 1. grid_point is diagonal to from_node
        if (
                (grid_points[0].position_x == from_node_x + 1 or
                 grid_points[0].position_x == from_node_x - 1)
                and (grid_points[0].position_y == from_node_y + 1 or
                     grid_points[0].position_y == from_node_y - 1)
        ):
            raise ValueError("Diagonal: from_node is diagonal to first grid_point")

    @staticmethod
    def is_last_grid_point_adjacent(to_node: Node, grid_points: list[GridPoint]) -> None:
        """Check if  last GridPoint is adjacent to to_node."""
        # test if the last grid_point is next to from_node
        to_node_x = to_node.grid_point[0].position_x
        if not (
                grid_points[-1].position_x == to_node_x
                or grid_points[-1].position_x == to_node_x + 1
                or grid_points[-1].position_x == to_node_x - 1
        ):
            raise ValueError("X-Position: to_node is not next to last grid_point")

        to_node_y = to_node.grid_point[0].position_y
        if not (
                grid_points[-1].position_y == to_node_y
                or grid_points[-1].position_y == to_node_y + 1
                or grid_points[-1].position_y == to_node_y - 1
        ):
            raise ValueError("Y-Position: to_node is not next to last grid_point")

        # test if the last grid_point is diagonal to from_node
        if (
                (grid_points[-1].position_x == to_node_x + 1 or
                 grid_points[-1].position_x == to_node_x - 1)
                and (grid_points[-1].position_y == to_node_y + 1 or
                     grid_points[-1].position_y == to_node_y - 1)
        ):
            raise ValueError("Diagonal: to_node is diagonal to last grid_point")

    @staticmethod
    def are_grid_points_adjacent(grid_points: list[GridPoint]) -> None:
        """Check if all GridPoints are adjacent to each other."""
        for i in range(len(grid_points) - 1):
            point1 = grid_points[i]
            point1_x = grid_points[i].position_x
            point1_y = grid_points[i].position_y
            point2 = grid_points[i + 1]
            point2_x = grid_points[i + 1].position_x
            point2_y = grid_points[i + 1].position_y

            # test if GridPoints are next to each other
            if not (
                    point1_x == point2_x
                    or point1_x == point2_x + 1
                    or point1_x == point2_x - 1
            ):
                raise ValueError(f"X-Position: GridPoint {point1.grid_point_id} "
                                 f"is not next to GridPoint {point2.grid_point_id}")

            if not (
                    point1_y == point2_y
                    or point1_y == point2_y + 1
                    or point1_y == point2_y - 1
            ):
                raise ValueError(f"Y-Position: GridPoint {point1.grid_point_id} "
                                 f"is not next to GridPoint {point2.grid_point_id}")

            # test if GridPoints are diagonal to each other
            if (
                    (point1_x == point2_x + 1 or
                     point1_x == point2_x - 1)
                    and (point1_y == point2_y + 1 or
                         point1_y == point2_y - 1)
            ):
                raise ValueError(f"Diagonal: GridPoint {point1.grid_point_id} "
                                 f"is diagonal to GridPoint {point2.grid_point_id}")
