"""Schema constants for the trading architecture program foundation."""

SCHEMA_VERSION = "trading_architecture_program.v1"
PROGRAM_NAME = "Trading System Architecture Program"
PROGRAM_STATUS = "Architecture Program Foundation Only"
ARCHITECTURE_ONLY_FLAGS = {
    "architecture_only": True,
    "research_only": True,
    "local_only": True,
    "not_implemented": True,
    "no_execution_capability": True,
    "no_broker_capability": True,
    "no_trading_capability": True,
    "no_broker_api": True,
    "no_broker_adapter": True,
    "no_pocket_option_login": True,
    "no_credentials": True,
    "no_browser_automation": True,
    "no_order_placement": True,
    "no_live_trading": True,
    "no_money_handling": True,
    "no_external_connectivity": True,
}
FORBIDDEN_SOURCE_TERMS = (
    "import " + "selenium",
    "from " + "selenium",
    "sync_" + "playwright",
    "async_" + "playwright",
    "web" + "driver",
    "place_" + "order(",
    "submit_" + "order(",
    "send_" + "order(",
    "api_" + "key=",
    "secret_" + "key=",
    "pass" + "word=",
)
