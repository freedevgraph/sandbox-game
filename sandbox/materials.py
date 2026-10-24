"""Material definitions: ids, colours, and movement rules.

Each material owns the rules for where it *tries* to move; the world is
responsible for bounds checks and for actually moving the particle. Adding a
new material therefore means adding an id, a spec, and (if it moves) a target
function.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import IntEnum
from typing import Callable, Iterable

EMPTY = -1

Coord = tuple[int, int]
Targets = Callable[[int, int, random.Random], Iterable[Coord]]


class Material(IntEnum):
    SAND = 0
    WATER = 1
    STONE = 2


def powder_targets(x: int, y: int, rng: random.Random) -> list[Coord]:
    """Straight down first, then the two diagonals, in random order."""
    diagonals = [(x - 1, y + 1), (x + 1, y + 1)]
    rng.shuffle(diagonals)
    return [(x, y + 1)] + diagonals


def liquid_targets(x: int, y: int, rng: random.Random) -> list[Coord]:
    """Fall down, and occasionally spill sideways."""
    spread = 0.35
    candidates = [(x, y + 1)]
    sides = []
    if rng.random() < spread:
        sides.append((x - 1, y))
    if rng.random() < spread:
        sides.append((x + 1, y))
    rng.shuffle(sides)
    candidates.extend(sides)
    return candidates


@dataclass(frozen=True)
class MaterialSpec:
    """A particle type. ``targets is None`` means the material never moves."""

    name: str
    color: tuple[int, int, int]
    targets: Targets | None = None


MATERIALS: dict[int, MaterialSpec] = {
    Material.SAND: MaterialSpec("sand", (222, 184, 135), powder_targets),
    Material.WATER: MaterialSpec("water", (30, 90, 220), liquid_targets),
    Material.STONE: MaterialSpec("stone", (145, 145, 150)),   # static
}


def color_of(material: int) -> tuple[int, int, int]:
    return MATERIALS[material].color
