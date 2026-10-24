"""User preferences, remembered between runs in ``settings.json``.

The two input methods are:

- ``MOUSE``     every mouse button has a fixed material (the original scheme)
- ``KEYBOARD``  number keys pick a material, and the left button paints it

Corrupt or missing settings never stop the game from starting; anything that
cannot be read falls back to the defaults.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .materials import MATERIALS, Material

SETTINGS_PATH = Path("settings.json")

# Number-key order, 1-based: 1 -> sand, 2 -> water, 3 -> stone.
NUMBERED_MATERIALS = tuple(sorted(MATERIALS))


class InputMode(str, Enum):
    MOUSE = "mouse"
    KEYBOARD = "keyboard"

    @property
    def label(self) -> str:
        """Human-readable name, shown in the settings panel."""
        if self is InputMode.MOUSE:
            return "Mouse buttons"
        return "Number keys"


def material_for_number(number: int | None) -> Material | None:
    """Material bound to a 1-based number key, or None when out of range."""
    if number is None or not 1 <= number <= len(NUMBERED_MATERIALS):
        return None
    return NUMBERED_MATERIALS[number - 1]


@dataclass
class Settings:
    input_mode: InputMode = InputMode.MOUSE
    selected: Material = Material.SAND

    @property
    def hint(self) -> str:
        """The one-line controls hint drawn along the bottom of the window."""
        if self.input_mode is InputMode.MOUSE:
            return "LMB: sand | RMB: water | MMB: stone | Tab: settings"
        choices = " | ".join(
            f"{number}: {MATERIALS[material].name}"
            for number, material in enumerate(NUMBERED_MATERIALS, start=1)
        )
        return f"{choices} | LMB: paint | Tab: settings"

    @classmethod
    def load(cls, path: Path = SETTINGS_PATH) -> "Settings":
        defaults = cls()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return defaults
        if not isinstance(data, dict):
            return defaults

        try:
            mode = InputMode(data.get("input_mode", defaults.input_mode.value))
        except (ValueError, TypeError):
            mode = defaults.input_mode

        selected = defaults.selected
        saved_name = str(data.get("selected_material", "")).lower()
        for material, spec in MATERIALS.items():
            if spec.name == saved_name:
                selected = material
                break

        return cls(mode, selected)

    def save(self, path: Path = SETTINGS_PATH) -> None:
        data = {
            "input_mode": self.input_mode.value,
            "selected_material": MATERIALS[self.selected].name,
        }
        try:
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        except OSError:
            pass  # unwritable directory: the game still runs, just forgets
