"""The settings overlay: switch input method and pick the number-key material."""

from __future__ import annotations

import pygame

from .config import (
    PANEL_ACCENT,
    PANEL_BG,
    PANEL_BORDER,
    PANEL_HEIGHT,
    PANEL_MUTED,
    PANEL_TEXT,
    PANEL_WIDTH,
)
from .input import number_from_key
from .materials import MATERIALS
from .settings import InputMode, Settings, material_for_number

_MODES = (InputMode.MOUSE, InputMode.KEYBOARD)
_PAD = 20
_GAP = 10
_BUTTON_H = 34


class SettingsPanel:
    """A modal panel; the game loop pauses the world while ``open`` is true."""

    def __init__(self) -> None:
        self.open = False
        self.title_font = pygame.font.Font(None, 28)
        self.label_font = pygame.font.Font(None, 18)
        self.font = pygame.font.Font(None, 22)
        self._overlay = pygame.Surface((1, 1), pygame.SRCALPHA)
        self._mode_hits: list[tuple[pygame.Rect, InputMode]] = []
        self._material_hits: list[tuple[pygame.Rect, int]] = []

    def toggle(self) -> None:
        self.open = not self.open

    # -- input ---------------------------------------------------------
    def handle_event(self, event: pygame.event.Event, settings: Settings) -> None:
        if event.type == pygame.KEYDOWN:
            self._handle_key(event.key, settings)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            self._handle_click(event.pos, settings)

    def _handle_key(self, key: int, settings: Settings) -> None:
        if key in (pygame.K_TAB, pygame.K_ESCAPE):
            self.open = False
        elif key == pygame.K_m:
            settings.input_mode = InputMode.MOUSE
        elif key == pygame.K_k:
            settings.input_mode = InputMode.KEYBOARD
        else:
            material = material_for_number(number_from_key(key))
            if material is not None:
                settings.selected = material

    def _handle_click(self, pos: tuple[int, int], settings: Settings) -> None:
        for rect, mode in self._mode_hits:
            if rect.collidepoint(pos):
                settings.input_mode = mode
                return
        for rect, material in self._material_hits:
            if rect.collidepoint(pos):
                settings.selected = material
                return

    # -- drawing -------------------------------------------------------
    def draw(self, screen: pygame.Surface, settings: Settings) -> None:
        self._dim(screen)

        panel = pygame.Rect(0, 0, PANEL_WIDTH, PANEL_HEIGHT)
        panel.center = screen.get_rect().center
        pygame.draw.rect(screen, PANEL_BG, panel, border_radius=12)
        pygame.draw.rect(screen, PANEL_BORDER, panel, width=2, border_radius=12)

        left, right = panel.left + _PAD, panel.right - _PAD
        y = panel.top + _PAD

        y = self._text(screen, "Settings", (left, y), self.title_font, PANEL_TEXT) + 12

        # -- input method ----------------------------------------------
        y = self._text(screen, "INPUT METHOD", (left, y), self.label_font, PANEL_MUTED) + 6
        self._mode_hits = []
        button_w = (right - left - _GAP) // len(_MODES)
        for i, mode in enumerate(_MODES):
            rect = pygame.Rect(left + i * (button_w + _GAP), y, button_w, _BUTTON_H)
            self._mode_button(screen, rect, mode, settings.input_mode is mode)
            self._mode_hits.append((rect, mode))
        y += _BUTTON_H + 16

        # -- number-key material ---------------------------------------
        y = self._text(
            screen, "MATERIAL FOR NUMBER KEYS", (left, y), self.label_font, PANEL_MUTED
        ) + 6
        self._material_hits = []
        count = len(MATERIALS)
        button_w = (right - left - _GAP * (count - 1)) // count
        for i, material in enumerate(sorted(MATERIALS)):
            rect = pygame.Rect(left + i * (button_w + _GAP), y, button_w, _BUTTON_H)
            self._material_button(
                screen, rect, i + 1, material, settings.selected == material
            )
            self._material_hits.append((rect, material))
        y += _BUTTON_H + 16

        pygame.draw.line(screen, PANEL_BORDER, (left, y), (right, y))
        y += 10
        y = self._text(
            screen,
            "M / K: switch method     1-3: pick material",
            (left, y),
            self.label_font,
            PANEL_MUTED,
        ) + 2
        self._text(
            screen, "Tab or Esc: close", (left, y), self.label_font, PANEL_MUTED
        )

    def _dim(self, screen: pygame.Surface) -> None:
        if self._overlay.get_size() != screen.get_size():
            self._overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            self._overlay.fill((0, 0, 0, 150))
        screen.blit(self._overlay, (0, 0))

    def _text(
        self,
        screen: pygame.Surface,
        text: str,
        pos: tuple[int, int],
        font: pygame.font.Font,
        color: tuple[int, int, int],
    ) -> int:
        """Blit one line and return the y coordinate just below it."""
        image = font.render(text, True, color)
        screen.blit(image, pos)
        return pos[1] + image.get_height()

    def _mode_button(
        self, screen: pygame.Surface, rect: pygame.Rect, mode: InputMode, active: bool
    ) -> None:
        if active:
            pygame.draw.rect(screen, PANEL_ACCENT, rect, border_radius=6)
            color = (26, 26, 36)
        else:
            pygame.draw.rect(screen, PANEL_BORDER, rect, width=1, border_radius=6)
            color = PANEL_TEXT
        label = self.font.render(mode.label, True, color)
        screen.blit(label, label.get_rect(center=rect.center))

    def _material_button(
        self,
        screen: pygame.Surface,
        rect: pygame.Rect,
        number: int,
        material: int,
        active: bool,
    ) -> None:
        pygame.draw.rect(
            screen,
            PANEL_ACCENT if active else PANEL_BORDER,
            rect,
            width=2 if active else 1,
            border_radius=6,
        )
        number_label = self.label_font.render(str(number), True, PANEL_MUTED)
        screen.blit(number_label, number_label.get_rect(midleft=(rect.left + 8, rect.centery)))

        swatch = pygame.Rect(0, 0, 16, 16)
        swatch.center = (rect.left + 34, rect.centery)
        pygame.draw.rect(screen, MATERIALS[material].color, swatch)
        pygame.draw.rect(screen, PANEL_BORDER, swatch, width=1)

        name = self.font.render(MATERIALS[material].name, True, PANEL_TEXT)
        screen.blit(name, name.get_rect(midleft=(swatch.right + 8, rect.centery)))
