from __future__ import annotations

import time
import random

from tkinter import Tk, Canvas


class Point:
    def __init__(self, x: int, y: int) -> None:
        self._x = x
        self._y = y

    def __eq__(self, __value: Point) -> bool:
        if not isinstance(__value, Point):
            return False
        if __value._x == self.x and __value._y == self.y:
            return True
        return False


class Line:
    def __init__(self, p1: Point, p2: Point) -> None:
        self._p1 = p1
        self._p2 = p2
        self.width = 2

    def draw(self, canvas: Canvas, fill_color: str) -> None:
        canvas.create_line(self._p1._x, self._p1._y, self._p2._x,
                           self._p2._y, fill=fill_color, width=self.width)
        canvas.pack()

    def __eq__(self, __value: Line) -> bool:
        if not isinstance(__value, Line):
            return False
        if __value._p1 == self._p1 and __value._p2 == self._p2:
            return True
        return False


class Cell:
    def __init__(self, win: Window = None, I=0, J=0, p1: Point = None, p2: Point = None) -> None:
        self._x1 = p1._x if p1 else 0
        self._x2 = p2._x if p2 else 0
        self._y1 = p1._y if p1 else 0
        self._y2 = p2._y if p2 else 0
        self._I = I
        self._J = J
        self._win = win
        self._line_color = "black"
        self.has_left_wall = True
        self.has_right_wall = True
        self.has_top_wall = True
        self.has_bottom_wall = True
        self.left_wall: Line = None
        self.right_wall: Line = None
        self.top_wall: Line = None
        self.bottom_wall: Line = None
        self._left_wall = None  # ID
        self._right_wall = None  # ID
        self._top_wall = None  # ID
        self._bottom_wall = None  # ID
        self.visited = False

    def draw(self, p1: Point = None, p2: Point = None) -> Cell:
        self._update_walls()
        if p1:
            self._x1 = p1._x
            self._y1 = p1._y
        if p2:
            self._x2 = p2._x
            self._y2 = p2._y
        if self.has_top_wall:
            self.top_wall = Line(Point(self._x1, self._y1),
                                 Point(self._x2, self._y1))
            self.top_wall.draw(self._win._canvas, self._line_color)
        if self.has_right_wall:
            self.right_wall = Line(Point(self._x2, self._y1),
                                   Point(self._x2, self._y2))
            self.right_wall.draw(self._win._canvas, self._line_color)
        if self.has_bottom_wall:
            self.bottom_wall = Line(Point(self._x2, self._y2),
                                    Point(self._x1, self._y2))
            self.bottom_wall.draw(self._win._canvas, self._line_color)
        if self.has_left_wall:
            self.left_wall = Line(Point(self._x1, self._y2),
                                  Point(self._x1, self._y1))
            self.left_wall.draw(self._win._canvas, self._line_color)
        return self

    def draw_move(self, to_cell: Cell, undo=False) -> None:
        line_color = "gray" if undo else "red"
        p1 = Point((self._x2 - self._x1) // 2 + self._x1,
                   (self._y2 - self._y1) // 2 + self._y1)
        p2 = Point((to_cell._x2 - to_cell._x1) // 2 + to_cell._x1,
                   (to_cell._y2 - to_cell._y1) // 2 + to_cell._y1)
        line = Line(p1, p2)
        line.draw(self._win._canvas, fill_color=line_color)

    def _update_walls(self) -> None:
        if self._left_wall and not self.has_left_wall:
            self._win._canvas.delete(self._left_wall)
            self._left_wall = None
            self.left_wall = None
        if self._right_wall and not self.has_right_wall:
            self._win._canvas.delete(self._right_wall)
            self._right_wall = None
            self.right_wall = None
        if self._top_wall and not self.has_top_wall:
            self._win._canvas.delete(self._top_wall)
            self._top_wall = None
            self.top_wall = None
        if self._bottom_wall and not self.has_bottom_wall:
            self._win._canvas.delete(self._bottom_wall)
            self._bottom_wall = None
            self.bottom_wall = None

    def break_down_wall(self, to_cell: Cell = None, direction: str = None) -> None:
        # Break walls
        if direction == "left":
            self.has_left_wall = False
            to_cell.has_right_wall = False
        elif direction == "right":
            self.has_right_wall = False
            to_cell.has_left_wall = False
        elif direction == "top":
            self.has_top_wall = False
            to_cell.has_bottom_wall = False
        elif direction == "bottom":
            self.has_bottom_wall = False
            to_cell.has_top_wall = False

        # Update
        self._update_walls()
        to_cell._update_walls()

    def _get_walls(self) -> dict:
        return {
            "left": self.left_wall,
            "right": self.right_wall,
            "top": self.top_wall,
            "bottom": self.bottom_wall
        }

    def can_go_to(self, cell: Cell, direction) -> bool:
        if cell.visited:
            return False
        walls = self._get_walls()
        target_walls = cell._get_walls()
        if direction == "left":
            return not walls["left"] and not target_walls["right"]
        elif direction == "right":
            return not walls["right"] and not target_walls["left"]
        elif direction == "top":
            return not walls["top"] and not target_walls["bottom"]
        elif direction == "bottom":
            return not walls["bottom"] and not target_walls["top"]
        else:
            raise Exception("Invalid direction")


class Maze:
    def __init__(
        self,
        x1=10,
        y1=10,
        width=800,
        height=600,
        num_rows=0,
        num_cols=0,
        win=None,
        seed=None
    ) -> None:
        self._x1 = x1
        self._y1 = y1
        self._width = width
        self._height = height
        self._num_rows = num_rows
        self._num_cols = num_cols
        self._cell_size_x = (self._width - self._x1*2) // num_cols
        self._cell_size_y = (self._height - self._y1*2) // num_rows
        self._win: Window = win
        self._cells = []

        if seed is not None:
            random.seed(seed)

        self._create_cells()
        self._break_entrance_and_exit(draw=False)

    def _create_cells(self) -> None:
        for I in range(0, self._num_cols):
            column = []
            for J in range(0, self._num_rows):
                cell = Cell(self._win, I=I, J=J)
                column.append(cell)
            self._cells.append(column)

    def _draw_cell(self, I, J) -> None:
        x1 = self._x1 + I * self._cell_size_x
        x2 = x1 + self._cell_size_x
        y1 = self._y1 + J * self._cell_size_y
        y2 = y1 + self._cell_size_y
        cell: Cell = self._cells[I][J]
        cell.draw(Point(x1, y1), Point(x2, y2))

    def _draw_cells(self) -> None:
        for i in range(len(self._cells)):
            for j in range(len(self._cells[i])):
                self._draw_cell(i, j)

    def _animate(self, interval=0.02, cells=None) -> None:
        if isinstance(cells, list):
            cell: Cell
            for cell in cells:
                self._draw_cell(cell._I, cell._J)
                time.sleep(interval)
                self._win.redraw()
        else:
            for i in range(len(self._cells)):
                for j in range(len(self._cells[i])):
                    self._draw_cell(i, j)
                    time.sleep(interval)
                    self._win.redraw()

    def _break_entrance_and_exit(self, draw=True) -> None:
        entrance: Cell = self._cells[0][0]
        exit: Cell = self._cells[len(self._cells) - 1][len(self._cells[0]) - 1]
        entrance.has_bottom_wall = False
        entrance.has_left_wall = False
        entrance.has_right_wall = False
        entrance.has_top_wall = False
        exit.has_bottom_wall = False
        exit.has_left_wall = False
        exit.has_right_wall = False
        exit.has_top_wall = False
        if draw:
            entrance.draw()
            exit.draw()

    def _get_neighbors(self, I, J) -> dict:
        return {
            "left": self._cells[I-1][J] if I > 0 else None,
            "right": self._cells[I+1][J] if I < len(self._cells) - 1 else None,
            "top": self._cells[I][J-1] if J > 0 else None,
            "bottom": self._cells[I][J+1] if J < len(self._cells[I]) - 1 else None
        }

    def _break_walls_r(self, I, J) -> None:
        cell: Cell = self._cells[I][J]
        cell.visited = True

        while True:
            possible_routes = []
            neighbors = self._get_neighbors(I, J)
            for direction, neighbor_cell in neighbors.items():
                if neighbor_cell and not neighbor_cell.visited:
                    possible_routes.append(
                        (neighbor_cell._I, neighbor_cell._J, direction))

            if len(possible_routes):
                idx = random.randint(0, len(possible_routes) - 1)
                chosen_route = possible_routes.pop(idx)
                target_cell: Cell = self._cells[chosen_route[0]
                                                ][chosen_route[1]]
                # Break down walls
                cell.break_down_wall(to_cell=target_cell,
                                     direction=chosen_route[2])
                self._break_walls_r(chosen_route[0], chosen_route[1])
            else:
                break

    def _reset_cells_visited(self) -> None:
        for col in self._cells:
            for cell in col:
                cell.visited = False

    def solve(self) -> None:
        """Solve the maze"""
        self._solve_r(0, 0)

    def _solve_r(self, I, J) -> None:
        """Recursive helper function for solving"""
        cell: Cell = self._cells[I][J]
        cell.visited = True
        self._animate(cells=[cell])

        if I == len(self._cells) - 1 and J == len(self._cells[I]) - 1:
            return True

        neighbors = self._get_neighbors(I, J)
        for direction, neighbor_cell in neighbors.items():
            if neighbor_cell and cell.can_go_to(neighbor_cell, direction):
                cell.draw_move(to_cell=neighbor_cell)
                solved = self._solve_r(neighbor_cell._I, neighbor_cell._J)
                if solved:
                    return True
                cell.draw_move(to_cell=neighbor_cell, undo=True)


class Window:
    def __init__(self, width, height, title) -> None:
        self._width = width
        self._height = height
        self._title = title
        self._running = False

        self.__root = Tk()
        self.__root.geometry(f'{width}x{height}')
        self.__root.title(title)
        self._canvas = Canvas(self.__root, width=width, height=height)
        self._canvas.pack()

        # Connect window close to our close method
        self.__root.protocol("WM_DELETE_WINDOW", self.close)

    def redraw(self) -> None:
        self.__root.update_idletasks()
        self.__root.update()

    def wait_for_close(self) -> None:
        self._running = True
        while self._running:
            self.redraw()

    def close(self) -> None:
        self._running = False

    def draw_line(self, line: Line, fill_color: str) -> None:
        line.draw(self._canvas, fill_color=fill_color)


if __name__ == "__main__":
    win = Window(800, 600, "Maze Solver")

    # Setup and draw a maze
    maze = Maze(width=800, height=600, num_cols=20, num_rows=20, win=win)
    maze._break_walls_r(0, 0)
    maze._animate(interval=0.001)

    # Solve the maze
    maze._reset_cells_visited()
    maze.solve()

    win.wait_for_close()
