"""Run local broker adapter diagnostics."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from loguru import logger  # noqa: E402

from app.brokers.demo_adapter import DemoBrokerAdapter  # noqa: E402
from app.config.settings import Settings  # noqa: E402
from app.logging.logger import configure_logging  # noqa: E402
from app.runtime.broker_runtime import BrokerRuntime  # noqa: E402


def main() -> None:
    """Validate demo broker lifecycle, health, latency, and reconnect behavior."""
    settings = Settings()
    configure_logging(settings.log_level, settings.log_file_path)

    config_path = PROJECT_ROOT / "configs" / "brokers" / "mock_latency.yaml"
    broker = DemoBrokerAdapter.from_yaml(config_path)
    runtime = BrokerRuntime(broker)

    runtime.initialize()
    capabilities = broker.get_capabilities().to_dict()
    first_health = runtime.heartbeat().to_dict()
    broker.reconnect()
    second_health = runtime.heartbeat().to_dict()
    diagnostics = runtime.diagnostics()
    runtime.shutdown()

    payload = {
        "capabilities": capabilities,
        "first_health": first_health,
        "second_health": second_health,
        "diagnostics": diagnostics.__dict__,
    }
    logger.info("Broker diagnostics: {}", payload)
    print(payload)


if __name__ == "__main__":
    main()
