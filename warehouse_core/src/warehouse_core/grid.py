"""Occupancy grid map: loading from map_server files and coordinate conversion."""
import os
from dataclasses import dataclass
from typing import List, Tuple

import yaml

FREE = 0
OCCUPIED = 100
UNKNOWN = -1


@dataclass(frozen=True)
class GridMap:
    """Row-major grid; row 0 is the bottom row (y = origin_y), as in nav_msgs/OccupancyGrid."""

    width: int
    height: int
    resolution: float
    origin_x: float
    origin_y: float
    data: Tuple[int, ...]

    def coord_to_index(self, x: float, y: float) -> int:
        index_x = int((x - self.origin_x) / self.resolution)
        index_y = int((y - self.origin_y) / self.resolution)
        return int(index_y * self.width + index_x)

    def index_to_coords(self, index: int) -> Tuple[float, float]:
        index_x = index % self.width
        index_y = index // self.width
        x = index_x * self.resolution + self.origin_x
        y = index_y * self.resolution + self.origin_y
        return x, y


def load_map(yaml_path: str) -> GridMap:
    """Load a map in map_server format (YAML + PGM image)."""
    with open(yaml_path, encoding="utf-8") as f:
        meta = yaml.safe_load(f)

    image_path = os.path.join(os.path.dirname(yaml_path), meta["image"])
    width, height, max_value, pixels = read_pgm(image_path)

    negate = bool(meta.get("negate", 0))
    occupied_thresh = float(meta["occupied_thresh"])
    free_thresh = float(meta["free_thresh"])

    data = [UNKNOWN] * (width * height)
    for image_row in range(height):
        grid_row = height - 1 - image_row
        for col in range(width):
            pixel = pixels[image_row * width + col]
            occupancy = pixel / max_value if negate else (max_value - pixel) / max_value
            if occupancy > occupied_thresh:
                value = OCCUPIED
            elif occupancy < free_thresh:
                value = FREE
            else:
                value = UNKNOWN
            data[grid_row * width + col] = value

    origin_x, origin_y = meta["origin"][0], meta["origin"][1]
    return GridMap(width, height, float(meta["resolution"]), float(origin_x), float(origin_y), tuple(data))


def read_pgm(path: str) -> Tuple[int, int, int, List[int]]:
    """Read a binary (P5) or text (P2) PGM image. Returns width, height, max value, pixels top-down."""
    with open(path, "rb") as f:
        content = f.read()

    tokens: List[bytes] = []
    position = 0
    while len(tokens) < 4:
        while content[position:position + 1].isspace():
            position += 1
        if content[position:position + 1] == b"#":
            position = content.index(b"\n", position) + 1
            continue
        start = position
        while not content[position:position + 1].isspace():
            position += 1
        tokens.append(content[start:position])

    magic = tokens[0]
    width, height, max_value = int(tokens[1]), int(tokens[2]), int(tokens[3])
    count = width * height

    if magic == b"P5":
        raw = content[position + 1:position + 1 + count]
        pixels = list(raw)
    elif magic == b"P2":
        pixels = [int(v) for v in content[position:].split()[:count]]
    else:
        raise ValueError("Unsupported PGM format: {!r}".format(magic))

    if len(pixels) != count:
        raise ValueError("PGM {} has {} pixels, expected {}".format(path, len(pixels), count))
    return width, height, max_value, pixels
