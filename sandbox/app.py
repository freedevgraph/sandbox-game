"""pygame setup and the main loop."""

import random

import pygame

from .config import CAPTION, FPS, HEIGHT, WIDTH
from .input import handle_event, paint_from_held_buttons
from .panel import SettingsPanel
from .renderer import Renderer
from .settings import Settings
from .world import World


def _init_pygame() -> None:
    """Bring up only the pygame subsystems the game actually uses.

    ``pygame.init()`` also starts the audio mixer and joystick drivers, which
    is the slowest part of startup and something this game never touches.
    """
    pygame.display.init()
    pygame.font.init()


class Game:
    def __init__(self) -> None:
        _init_pygame()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(CAPTION)
        self.clock = pygame.time.Clock()
        self.world = World()
        self.settings = Settings.load()
        self.panel = SettingsPanel()
        self.renderer = Renderer(self.screen)
        self.rng = random.Random()

    def run(self) -> None:
        running = True
        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif self.panel.open:
                        self.panel.handle_event(event, self.settings)
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                        self.panel.open = True
                    else:
                        handle_event(event, self.world, self.settings)

                if not self.panel.open:
                    pressed = pygame.mouse.get_pressed()
                    paint_from_held_buttons(self.world, pressed, self.settings)
                    self.world.step(self.rng)

                self.renderer.draw(self.world, self.settings)
                if self.panel.open:
                    self.panel.draw(self.screen, self.settings)

                pygame.display.flip()
                self.clock.tick(FPS)
        finally:
            self.settings.save()
            pygame.quit()
