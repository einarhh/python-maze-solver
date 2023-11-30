import unittest

from maze import Maze


class Tests(unittest.TestCase):
    def test_maze_create_cells(self):
        num_cols = 12
        num_rows = 10
        m1 = Maze(width=800, height=600, num_cols=num_cols, num_rows=num_rows)
        self.assertEqual(
            len(m1._cells),
            num_cols,
        )
        self.assertEqual(
            len(m1._cells[0]),
            num_rows,
        )

    def test_maze_reset_visited(self):
        m1 = Maze(width=800, height=600, num_cols=12, num_rows=10)
        for col in m1._cells:
            for cell in col:
                cell.visited = True
        m1._reset_cells_visited()
        for col in m1._cells:
            for cell in col:
                self.assertFalse(cell.visited)


if __name__ == "__main__":
    unittest.main()
