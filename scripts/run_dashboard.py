"""Run the local research dashboard."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config.settings import Settings  # noqa: E402
from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.dashboard.service import load_dashboard_config  # noqa: E402
from app.logging.logger import configure_logging  # noqa: E402


app = create_dashboard_app(PROJECT_ROOT)


def main() -> None:
    """Start uvicorn or run a non-blocking smoke check."""
    parser = argparse.ArgumentParser(description="Run the local research dashboard")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Create the app without starting a server",
    )
    args = parser.parse_args()

    settings = Settings()
    configure_logging(settings.log_level, settings.log_file_path)
    config = load_dashboard_config(PROJECT_ROOT)
    if args.check:
        routes = sorted(route.path for route in app.routes)
        print(
            {
                "dashboard": "ok",
                "routes": routes,
                "host": config.host,
                "port": config.port,
            }
        )
        return

    import uvicorn

    uvicorn.run("scripts.run_dashboard:app", host=config.host, port=config.port, reload=False)


if __name__ == "__main__":
    main()
