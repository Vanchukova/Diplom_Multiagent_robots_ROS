import os

import pytest

from warehouse_core.grid import FREE, OCCUPIED, UNKNOWN, GridMap, load_map, read_pgm

MAPS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "maps")


@pytest.fixture
def warehouse():
    return load_map(os.path.join(MAPS_DIR, "warehouse_1m.yaml"))


def test_warehouse_map_size_and_origin(warehouse):
    assert (warehouse.width, warehouse.height) == (60, 100)
    assert warehouse.resolution == 1.0
    assert (warehouse.origin_x, warehouse.origin_y) == (-30.0, -50.0)


def test_warehouse_map_border_is_occupied(warehouse):
    bottom_row = warehouse.data[:warehouse.width]
    assert all(cell == OCCUPIED for cell in bottom_row)


@pytest.mark.parametrize(
    "x, y, expected_index",
    [
        (-30.0, -50.0, 0),
        (-29.0, -50.0, 1),
        (-30.0, -49.0, 60),
        (-23.0, 40.0, 90 * 60 + 7),
        (-22.5, 40.9, 90 * 60 + 7),
    ],
)
def test_coord_to_index(warehouse, x, y, expected_index):
    assert warehouse.coord_to_index(x, y) == expected_index


def test_index_to_coords_returns_cell_corner(warehouse):
    assert warehouse.index_to_coords(90 * 60 + 7) == (-23.0, 40.0)


def test_round_trip_for_every_cell(warehouse):
    for index in range(warehouse.width * warehouse.height):
        x, y = warehouse.index_to_coords(index)
        assert warehouse.coord_to_index(x, y) == index


def test_image_top_row_becomes_last_grid_row(tmp_path):
    (tmp_path / "m.pgm").write_text("P2\n2 2\n255\n0 254\n254 254\n")
    (tmp_path / "m.yaml").write_text(
        "image: m.pgm\nresolution: 0.5\norigin: [1.0, 2.0, 0.0]\n"
        "negate: 0\noccupied_thresh: 0.65\nfree_thresh: 0.196\n"
    )
    grid = load_map(str(tmp_path / "m.yaml"))
    assert grid.data == (FREE, FREE, OCCUPIED, FREE)
    assert grid == GridMap(2, 2, 0.5, 1.0, 2.0, (FREE, FREE, OCCUPIED, FREE))


def test_grey_pixel_is_unknown(tmp_path):
    (tmp_path / "m.pgm").write_text("P2\n1 1\n255\n128\n")
    (tmp_path / "m.yaml").write_text(
        "image: m.pgm\nresolution: 1\norigin: [0, 0, 0]\n"
        "negate: 0\noccupied_thresh: 0.65\nfree_thresh: 0.196\n"
    )
    assert load_map(str(tmp_path / "m.yaml")).data == (UNKNOWN,)


def test_read_binary_pgm_with_comment(tmp_path):
    (tmp_path / "b.pgm").write_bytes(b"P5\n# comment\n3 1\n255\n" + bytes([0, 128, 254]))
    assert read_pgm(str(tmp_path / "b.pgm")) == (3, 1, 255, [0, 128, 254])
