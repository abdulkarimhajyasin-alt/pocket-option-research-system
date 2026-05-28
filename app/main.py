"""Application entry point for the Phase 1 research platform foundation."""

from app.runtime.bot_runner import BotRunner


def main() -> None:
    """Run the minimal demo execution flow."""
    runner = BotRunner()
    runner.run()


if __name__ == "__main__":
    main()
