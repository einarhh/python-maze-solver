from __future__ import annotations

import time
import random

from tkinter import Tk, BOTH, Canvas


class Point:
    def __init__(self, x: int, y: int) -> None:
        self._x = x
        self._y = y


class Line:
    def __init__(self, p1: Point, p2: Point) -> None:
        self._p1 = p1
        self._p2 = p2
        self.width = 2

    def draw(self, canvas: Canvas, fill_color: str) -> None:
        canvas.create_line(self._p1._x, self._p1._y, self._p2._x,
                           self._p2._y, fill=fill_color, width=self.width)
        canvas.pack()


class Cell:
    def __init__(self, win: Window = None, p1: Point = None, p2: Point = None) -> None:
        self._x1 = p1._x if p1 else 0
        self._x2 = p2._x if p2 else 0
        self._y1 = p1._y if p1 else 0
        self._y2 = p2._y if p2 else 0
        self._win = win
        self._line_color = "black"
        self.has_left_wall = True
        self.has_right_wall = True
        self.has_top_wall = True
        self.has_bottom_wall = True
        self._left_wall = None
        self._right_wall = None
        self._top_wall = None
        self._bottom_wall = None
        self.visited = False

    def draw(self, p1: Point = None, p2: Point = None):
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

    def draw_move(self, to_cell: Cell, undo=False):
        line_color = "gray" if undo else "red"
        p1 = Point((self._x2 - self._x1) // 2 + self._x1,
                   (self._y2 - self._y1) // 2 + self._y1)
        p2 = Point((to_cell._x2 - to_cell._x1) // 2 + to_cell._x1,
                   (to_cell._y2 - to_cell._y1) // 2 + to_cell._y1)
        line = Line(p1, p2)
        line.draw(self._win._canvas, fill_color=line_color)

    def _update_walls(self):
        if self._left_wall and not self.has_left_wall:
            self._win._canvas.delete(self._left_wall)
            self._left_wall = None
        if self._right_wall and not self.has_right_wall:
            self._win._canvas.delete(self._right_wall)
            self._right_wall = None
        if self._top_wall and not self.has_top_wall:
            self._win._canvas.delete(self._top_wall)
            self._top_wall = None
        if self._bottom_wall and not self.has_bottom_wall:
            self._win._canvas.delete(self._bottom_wall)
            self._bottom_wall = None

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


class Maze:
    def __init__(
        self,
        x1=10,
        y1=10,
        width=800,
        height=600,
        num_rows=0,
        num_cols=0,
        # cell_size_x,
        # cell_size_y,
        win=None,
        seed=None
    ):
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

    def _create_cells(self):
        for _ in range(0, self._num_cols):
            column = []
            for _ in range(0, self._num_rows):
                cell = Cell(self._win)
                column.append(cell)
            self._cells.append(column)

    def _draw_cell(self, I, J):
        x1 = self._x1 + I * self._cell_size_x
        x2 = x1 + self._cell_size_x
        y1 = self._y1 + J * self._cell_size_y
        y2 = y1 + self._cell_size_y
        cell: Cell = self._cells[I][J]
        cell.draw(Point(x1, y1), Point(x2, y2))

    def _draw_cells(self):
        for i in range(len(self._cells)):
            for j in range(len(self._cells[i])):
                self._draw_cell(i, j)

    def _animate(self, interval=0.02):
        for i in range(len(self._cells)):
            for j in range(len(self._cells[i])):
                self._draw_cell(i, j)
                time.sleep(interval)
                self._win.redraw()

    def _break_entrance_and_exit(self, draw=True):
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

    def _break_walls_r(self, I, J):
        cell: Cell = self._cells[I][J]
        cell.visited = True

        # Found exit
        if I == len(self._cells) - 1 and J == len(self._cells[I]) - 1:
            print("Exit")

        while True:
            possible_routes = []
            # Left
            if I > 0 and not self._cells[I-1][J].visited:
                possible_routes.append(
                    (I-1, J, "left"))
            # Top
            if J > 0 and not self._cells[I][J-1].visited:
                possible_routes.append(
                    (I, J-1, "top"))
            # Right
            if I < len(self._cells) - 1 and not self._cells[I+1][J].visited:
                possible_routes.append(
                    (I+1, J, "right"))
            # Bottom
            if J < len(self._cells[I]) - 1 and not self._cells[I][J+1].visited:
                possible_routes.append(
                    (I, J+1, "bottom"))

            if len(possible_routes):
                chosen_route = possible_routes.pop(random.randint(
                    0, len(possible_routes) - 1))
                target_cell: Cell = self._cells[chosen_route[0]
                                                ][chosen_route[1]]
                # Break down walls
                cell.break_down_wall(to_cell=target_cell,
                                     direction=chosen_route[2])
                self._break_walls_r(chosen_route[0], chosen_route[1])
            else:
                break

    def _reset_cells_visited(self):
        for col in self._cells:
            for cell in col:
                cell.visited = False


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
    win = Window(800, 600, "Title")
    """
    cell1 = Cell(win, Point(20, 20), Point(200, 100)).draw()

    cell = Cell(win, Point(300, 10), Point(350, 20))
    cell.has_bottom_wall = False
    cell.has_left_wall = False
    cell.draw()
    cell1.draw_move(cell)
    """

    # Draw the maze
    maze = Maze(width=800, height=600, num_cols=10, num_rows=10, win=win)
    maze._break_walls_r(0, 0)
    maze._animate(interval=0.01)

    # Reset visited
    maze._reset_cells_visited()

    win.wait_for_close()
