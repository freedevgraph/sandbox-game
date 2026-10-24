"""Drawing the world to the screen."""

import pygame

from .config import BG, HINT_COLOR, HINT_MARGIN
from .materials import EMPTY, MATERIALS
from .settings import InputMode, Settings
from .world import World


class Renderer:
    """Paints one cell per pixel, then scales the whole grid up in one blit."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.surface = pygame.Surface((1, 1))
        self.font = pygame.font.Font(None, 20)
        self.palette = {material: spec.color for material, spec in MATERIALS.items()}

    def draw(self, world: World, settings: Settings) -> None:
        if self.surface.get_size() != (world.width, world.height):
            self.surface = pygame.Surface((world.width, world.height))

        self.surface.fill(BG)
        for idx, material in enumerate(world.cells):
            if material != EMPTY:
                self.surface.set_at(
                    (idx % world.width, idx // world.width), self.palette[material]
                )

        # one cheap scale-up instead of thousands of blits
        pygame.transform.scale(self.surface, self.screen.get_size(), self.screen)
        self._draw_hint(settings)

    def _draw_hint(self, settings: Settings) -> None:
        inset, from_bottom = HINT_MARGIN
        y = self.screen.get_height() - from_bottom

        if settings.input_mode is InputMode.KEYBOARD:
            swatch = pygame.Rect(inset, y + 3, 12, 12)
            pygame.draw.rect(self.screen, MATERIALS[settings.selected].color, swatch)
            pygame.draw.rect(self.screen, HINT_COLOR, swatch, width=1)
            inset = swatch.right + 8

        hint = self.font.render(settings.hint, True, HINT_COLOR)
        self.screen.blit(hint, (inset, y))
