"""Occasional benchmark for the sandbox game.

Run it whenever you want a health check on the numbers that matter:

    python benchmark.py

What it measures
----------------

- **startup** - imports, pygame subsystem init, window creation, and the
  world/panel build. Startup is measured twice in fresh interpreters: once
  with the old full ``pygame.init()`` (which also starts the unused audio
  mixer and joysticks) and once with the selective init ``sandbox.app`` now
  performs, so you can see how much time the selective path saves.
- **simulation** - ``World.step`` per-frame cost at the default grid size,
  with a few thousand particles on the board, so you can tell whether there
  is still headroom against the 60 FPS target.
- **drawing** - ``Renderer.draw`` per-frame cost on a populated world.

A dummy video/audio driver is used so nothing opens a window on your desktop;
the real work (imports, module init, surface setup, simulation) is identical
to a real run.
"""

from __future__ import annotations

import os
import random
import statistics
import subprocess
import sys
import time

# Must be set before pygame is imported; keeps the benchmark headless.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_IMPORT_START = time.perf_counter()
import pygame  # noqa: E402
from sandbox.app import Game  # noqa: E402
from sandbox.config import FPS  # noqa: E402
from sandbox.materials import Material  # noqa: E402
from sandbox.world import World  # noqa: E402
IMPORT_TIME = time.perf_counter() - _IMPORT_START

WARMUP_FRAMES = 20
MEASURED_FRAMES = 120

FULL_INIT = (
    "import time; start = time.perf_counter(); "
    "import pygame; pygame.init(); "
    "pygame.display.set_mode((800, 600)); "
    "print(time.perf_counter() - start)"
)
SELECTIVE_INIT = (
    "import time; start = time.perf_counter(); "
    "import pygame; "
    "pygame.display.init(); pygame.font.init(); "
    "pygame.display.set_mode((800, 600)); "
    "print(time.perf_counter() - start)"
)


def ms(seconds: float) -> str:
    return f"{seconds * 1000:6.1f} ms"


def timed_subprocess(code: str) -> float:
    """Run one timing snippet in a fresh interpreter; return its wall time."""
    start = time.perf_counter()
    subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        check=True,
    )
    return time.perf_counter() - start


def paint_sample(rng: random.Random, world: World, clumps: int) -> int:
    """Drop sand/water/stone clumps so the sim has work to do; return count."""
    materials = (Material.SAND, Material.WATER, Material.STONE)
    for _ in range(clumps):
        x, y = rng.randrange(world.width), rng.randrange(world.height)
        world.paint(x, y, rng.choice(materials))
    return sum(1 for cell in world.cells if cell != -1)


def measure_startup() -> Game:
    print("== startup ==")
    print(f"package imports       {ms(IMPORT_TIME)}")

    env = os.environ | {"SDL_VIDEODRIVER": "dummy", "SDL_AUDIODRIVER": "dummy"}
    baseline = timed_subprocess("pass")
    full = timed_subprocess(FULL_INIT) - baseline
    selective = timed_subprocess(SELECTIVE_INIT) - baseline
    print(f"interpreter overhead  {ms(baseline)}")
    print(f"pygame.init() + window {ms(full)}  (old way)")
    print(f"selective init + window {ms(selective)}  (what app.py does now)")
    print(f"startup saved         {ms(max(0.0, full - selective))}")

    start = time.perf_counter()
    game = Game()
    build = time.perf_counter() - start
    print(f"Game() build          {ms(build)}")
    return game


def measure_step() -> None:
    print("== simulation ==")
    rng = random.Random(1234)
    world = World()
    particles = paint_sample(rng, world, clumps=500)

    samples: list[float] = []
    for i in range(WARMUP_FRAMES + MEASURED_FRAMES):
        start = time.perf_counter()
        world.step(rng)
        if i >= WARMUP_FRAMES:
            samples.append(time.perf_counter() - start)

    mean = statistics.fmean(samples)
    budget = 1 / FPS
    print(
        f"step at {particles} particles: mean {ms(mean)}, "
        f"median {ms(statistics.median(samples))}, max {ms(max(samples))} "
        f"({budget / mean:.1f} steps fit in one frame, "
        f"{mean / budget:.0%} of the {(1 / FPS) * 1000:.0f} ms frame)"
    )


def measure_draw(game: Game) -> None:
    print("== drawing ==")
    paint_sample(random.Random(99), game.world, clumps=400)

    samples: list[float] = []
    for i in range(WARMUP_FRAMES + MEASURED_FRAMES):
        start = time.perf_counter()
        game.renderer.draw(game.world, game.settings)
        if i >= WARMUP_FRAMES:
            samples.append(time.perf_counter() - start)

    mean = statistics.fmean(samples)
    budget = 1 / FPS
    print(
        f"draw mean {ms(mean)}, median {ms(statistics.median(samples))}, "
        f"max {ms(max(samples))} ({mean / budget:.0%} of the "
        f"{(1 / FPS) * 1000:.0f} ms frame)"
    )


def main() -> None:
    game = measure_startup()
    measure_step()
    measure_draw(game)
    pygame.quit()


if __name__ == "__main__":
    main()
