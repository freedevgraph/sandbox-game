import os
import random
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from sandbox.materials import Material, powder_targets, liquid_targets
from sandbox.input import HELD_MATERIALS
from sandbox.world import World


class TestSandboxFixes(unittest.TestCase):
    def test_powder_targets_order(self) -> None:
        rng = random.Random(42)
        for _ in range(50):
            targets = powder_targets(10, 10, rng)
            self.assertEqual(targets[0], (10, 11), "Straight down should always be the first candidate target")
            self.assertEqual(set(targets[1:]), {(9, 11), (11, 11)})

    def test_liquid_targets_unrestricted_and_shuffled(self) -> None:
        rng = random.Random(42)
        # Verify liquid targets at y=0 can include sideways coordinates (x-1, 0) or (x+1, 0)
        found_side = False
        for _ in range(100):
            targets = liquid_targets(10, 0, rng)
            self.assertEqual(targets[0], (10, 1))
            if len(targets) > 1:
                found_side = True
                self.assertIn(targets[1][1], (0, 1))
        self.assertTrue(found_side, "Liquid at y=0 should be able to offer sideways candidates")

    def test_held_materials(self) -> None:
        self.assertIn(1, HELD_MATERIALS)
        self.assertEqual(HELD_MATERIALS[1], Material.STONE)

    def test_world_paint_boundary(self) -> None:
        world = World(10, 10)
        # Painting at (-1, 5) with radius 1 should fill (0, 4), (0, 5), (0, 6)
        world.paint(-1, 5, Material.SAND, radius=1)
        self.assertEqual(world.get(0, 4), Material.SAND)
        self.assertEqual(world.get(0, 5), Material.SAND)
        self.assertEqual(world.get(0, 6), Material.SAND)


if __name__ == "__main__":
    unittest.main()
