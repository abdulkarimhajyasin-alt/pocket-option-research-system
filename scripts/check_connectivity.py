"""Run read-only connectivity diagnostics."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config.settings import Settings  # noqa: E402
from app.connectivity.csv_market_connector import CsvMarketDataConnector  # noqa: E402
from app.connectivity.errors import ConnectorUnsafeOperationError  # noqa: E402
from app.connectivity.registry import ConnectorRegistry  # noqa: E402
from app.connectivity.simulated_market_connector import SimulatedMarketConnector  # noqa: E402
from app.logging.logger import configure_logging  # noqa: E402
from app.runtime.connectivity_runtime import ConnectivityRuntime  # noqa: E402


def main() -> None:
    """Initialize connectors, validate ingestion, and print diagnostics."""
    settings = Settings()
    configure_logging(settings.log_level, settings.log_file_path)

    csv_config = PROJECT_ROOT / "configs" / "connectivity" / "csv_connector.yaml"
    simulated_config = PROJECT_ROOT / "configs" / "connectivity" / "simulated_connector.yaml"

    registry = ConnectorRegistry()
    registry.register("csv_market_connector", lambda: CsvMarketDataConnector.from_yaml(csv_config))
    registry.register(
        "simulated_market_connector",
        lambda: SimulatedMarketConnector.from_yaml(simulated_config),
    )

    csv_runtime = ConnectivityRuntime(registry.create("csv_market_connector"), stale_after_minutes=525600)
    simulated_runtime = ConnectivityRuntime(registry.create("simulated_market_connector"))
    csv_runtime.initialize()
    simulated_runtime.initialize()

    csv_runtime.heartbeat()
    simulated_runtime.heartbeat()
    csv_series, csv_validation = csv_runtime.fetch_and_validate("EURUSD", "1m", limit=25)
    simulated_series, simulated_validation = simulated_runtime.fetch_and_validate(
        "EURUSD",
        "5m",
        limit=20,
    )

    execution_unavailable = False
    try:
        csv_runtime.connector.place_trade()
    except ConnectorUnsafeOperationError:
        execution_unavailable = True

    diagnostics = {
        "registered_connectors": registry.names(),
        "csv": {
            "candles": len(csv_series),
            "validation": csv_validation.to_dict(),
            "diagnostics": csv_runtime.diagnostics().__dict__,
        },
        "simulated": {
            "candles": len(simulated_series),
            "validation": simulated_validation.to_dict(),
            "diagnostics": simulated_runtime.diagnostics().__dict__,
        },
        "execution_unavailable": execution_unavailable,
    }
    print(diagnostics)
    csv_runtime.shutdown()
    simulated_runtime.shutdown()


if __name__ == "__main__":
    main()
