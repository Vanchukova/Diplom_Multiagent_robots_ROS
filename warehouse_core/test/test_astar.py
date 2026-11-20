"""Behaviour of A* on small hand-made grids.

Tests marked xfail describe the correct behaviour for known bugs.
They will start passing when the bugs are fixed in step 2.
"""
import pytest

from warehouse_core.astar import astar

W = 100  # wall


def make_grid(rows):
    """rows are written top-down (as on screen); the grid stores row 0 at the bottom."""
    height = len(rows)
    width = len(rows[0])
    data = [cell for row in reversed(rows) for cell in row]
    return width, height, data


def index(width, x, y):
    return y * width + x


def plan(rows, start, goal):
    width, height, data = make_grid(rows)
    return astar(index(width, *start), index(width, *goal), width, height, data, 1, [0, 0, 0])


CORRIDOR = [
    [W, W, W, W, W, W],
    [W, 0, 0, 0, 0, W],
    [W, W, W, W, W, W],
]

OPEN_6x6 = [[0] * 6 for _ in range(6)]

WALL_WITH_GAP = [
    [W, W, W, W, W, W, W],
    [W, 0, 0, 0, 0, 0, W],
    [W, 0, W, W, W, 0, W],
    [W, 0, 0, 0, W, 0, W],
    [W, W, W, W, W, W, W],
]

CLOSED_ROOM = [
    [W, W, W, W, W],
    [W, 0, W, 0, W],
    [W, W, W, W, W],
]


def test_straight_corridor_path_excludes_start():
    path, found = plan(CORRIDOR, (1, 1), (4, 1))
    assert found is True
    assert path == [8, 9, 10, 10]


def test_start_equals_goal():
    path, found = plan(CORRIDOR, (2, 1), (2, 1))
    assert (path, found) == ([8], True)


def test_path_goes_around_wall_and_avoids_obstacles():
    width, _, data = make_grid(WALL_WITH_GAP)
    path, found = plan(WALL_WITH_GAP, (1, 1), (5, 1))
    assert found is True
    assert all(data[cell] < 90 for cell in path)
    assert index(width, 1, 3) in path
    assert path[-1] == index(width, 5, 1)


def test_current_behaviour_on_open_grid_is_a_staircase():
    path, found = plan(OPEN_6x6, (1, 1), (4, 4))
    assert found is True
    assert path == [8, 14, 15, 21, 22, 28, 28]


@pytest.mark.xfail(strict=True, reason="bug: returns a bare list when no path exists (step 2)")
def test_no_path_returns_empty_path_and_false():
    assert plan(CLOSED_ROOM, (1, 1), (3, 1)) == ([], False)


@pytest.mark.xfail(strict=True, reason="bug: goal cell is added to the path twice (step 2)")
def test_goal_appears_once():
    path, _ = plan(CORRIDOR, (1, 1), (4, 1))
    assert path.count(path[-1]) == 1


@pytest.mark.xfail(strict=True, reason="bug: diagonal step costs 2*sqrt(2) instead of sqrt(2) (step 2)")
def test_open_grid_uses_diagonal_moves():
    path, _ = plan(OPEN_6x6, (1, 1), (4, 4))
    assert set(path) - {7} == {14, 21, 28}
