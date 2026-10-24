"""The particle grid and the simulation step."""

from __future__ import annotations

import random

from .config import BRUSH_RADIUS, GRID_H, GRID_W
from .materials import EMPTY, MATERIALS


class World:
    """A flat grid of cells, where ``EMPTY`` means air."""

    def __init__(self, width: int = GRID_W, height: int = GRID_H) -> None:
        self.width = width
        self.height = height
        self.cells = [EMPTY] * (width * height)

    # -- queries ------------------------------------------------------
    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def index(self, x: int, y: int) -> int:
        return y * self.width + x

    def get(self, x: int, y: int) -> int:
        return self.cells[self.index(x, y)]

    def is_empty(self, x: int, y: int) -> bool:
        return self.get(x, y) == EMPTY

    # -- editing ------------------------------------------------------
    def paint(self, gx: int, gy: int, material: int, radius: int = BRUSH_RADIUS) -> None:
        """Fill empty cells in a square brush around the given cell."""
        for y in range(gy - radius, gy + radius + 1):
            for x in range(gx - radius, gx + radius + 1):
                if self.in_bounds(x, y) and self.is_empty(x, y):
                    self.cells[self.index(x, y)] = material

    def clear(self) -> None:
        self.cells = [EMPTY] * (self.width * self.height)

    # -- simulation ---------------------------------------------------
    def step(self, rng: random.Random) -> None:
        """Advance one tick.

        Iterating bottom-to-top means particles only ever move into cells that
        have already been visited, so nothing can be moved twice in one frame.
        """
        new_cells = self.cells[:]
        for idx in range(len(self.cells) - 1, -1, -1):
            material = self.cells[idx]
            spec = MATERIALS.get(material)
            if spec is None or spec.targets is None:   # air, or stone
                continue
            x, y = idx % self.width, idx // self.width
            for nx, ny in spec.targets(x, y, rng):
                if self.in_bounds(nx, ny) and new_cells[self.index(nx, ny)] == EMPTY:
                    new_cells[idx] = EMPTY
                    new_cells[self.index(nx, ny)] = material
                    break
        self.cells = new_cells
