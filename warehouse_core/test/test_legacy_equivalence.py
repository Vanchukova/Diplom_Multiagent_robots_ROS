"""The core must behave exactly like the original code it was moved from.

The original modules stay in a_star/scripts until the ROS 2 migration;
these tests are skipped once they are gone.
"""
import importlib
import os
import random
import re
import sys
import types

import pytest

from warehouse_core.astar import astar
from warehouse_core.grid import FREE, load_map

PACKAGE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_DIR = os.path.dirname(PACKAGE_DIR)
LEGACY_SCRIPTS = os.path.join(REPO_DIR, "a_star", "scripts")
LEGACY_PLANNER = os.path.join(LEGACY_SCRIPTS, "path_planner_robot_1.py")

pytestmark = pytest.mark.skipif(
    not os.path.exists(LEGACY_PLANNER), reason="original a_star scripts were removed"
)


@pytest.fixture(scope="module")
def legacy_astar():
    fake_rospy = types.ModuleType("rospy")
    fake_rospy.loginfo = lambda *args, **kwargs: None
    fake_rospy.logwarn = lambda *args, **kwargs: None

    saved = {name: sys.modules.get(name) for name in ("rospy", "alghorithms", "alghorithms.astar", "alghorithms.neighbors")}
    sys.modules["rospy"] = fake_rospy
    sys.path.insert(0, LEGACY_SCRIPTS)
    try:
        for name in ("alghorithms", "alghorithms.astar", "alghorithms.neighbors"):
            sys.modules.pop(name, None)
        yield importlib.import_module("alghorithms.astar").astar
    finally:
        sys.path.remove(LEGACY_SCRIPTS)
        for name, module in saved.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module


@pytest.fixture(scope="module")
def warehouse():
    return load_map(os.path.join(PACKAGE_DIR, "maps", "warehouse_1m.yaml"))


def legacy_costmap():
    with open(LEGACY_PLANNER, encoding="utf-8") as f:
        source = f.read()
    body = re.search(r"self\.costmap=\[(.*?)\]", source, re.S).group(1)
    return [int(value) for value in re.findall(r"-?\d+", body)]


def test_map_file_matches_costmap_in_planner(warehouse):
    assert list(warehouse.data) == legacy_costmap()


def test_coordinate_conversion_matches_planner(warehouse):
    origin_x, origin_y, resolution, width = -30, -50, 1, 60
    for x, y in [(-23.0, 40.0), (0.0, 0.0), (15.0, 24.6), (10.0, -47.4), (-25.52, 39.57)]:
        index_x = int((x - origin_x) / resolution)
        index_y = int((y - origin_y) / resolution)
        assert warehouse.coord_to_index(x, y) == int(index_y * width + index_x)


def sample_pairs(warehouse, count, seed=2024):
    rng = random.Random(seed)
    free_cells = [i for i, cell in enumerate(warehouse.data) if cell == FREE]
    return [(rng.choice(free_cells), rng.choice(free_cells)) for _ in range(count)]


def test_astar_matches_original_on_warehouse_map(legacy_astar, warehouse):
    costmap = list(warehouse.data)
    args = (warehouse.width, warehouse.height, costmap, 1, [-30, -50, 0])
    for start, goal in sample_pairs(warehouse, 40):
        assert astar(start, goal, *args) == legacy_astar(start, goal, *args), (start, goal)
