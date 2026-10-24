"""Entry point for the falling-sand sandbox: ``python game.py``."""

from sandbox.app import Game


def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()
