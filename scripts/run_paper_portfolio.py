"""Run the paper-only portfolio governance layer."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.paper_portfolio.service import PaperPortfolioService  # noqa: E402


def main() -> None:
    """Generate paper portfolio storage and reports."""
    run = PaperPortfolioService(PROJECT_ROOT).run()
    portfolio = run.result.portfolio
    print("Paper portfolio generated")
    print(f"total_orders={portfolio.total_orders}")
    print(f"health_score={portfolio.health_score}")
    print(f"stability_score={portfolio.stability_score}")
    print(f"portfolio_score={run.result.score}")
    print("paper_only=True")
    print("research_only=True")
    print("not_real_money=True")
    print(f"storage={run.storage_paths}")
    print(f"reports={run.report_paths}")


if __name__ == "__main__":
    main()
