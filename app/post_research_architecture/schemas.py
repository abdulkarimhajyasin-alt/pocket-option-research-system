"""Schema constants for post-research strategic architecture outputs."""

SCHEMA_VERSION = "post_research_architecture.v1"
CURRENT_PLATFORM_STATE = "Research Platform v1.0"
NEXT_PROGRAM_NAME = "Trading System Architecture Program"
FIRST_SAFE_NEXT_STEP = (
    "Complete documentation and metadata reconciliation, then decide whether to start "
    "a separate architecture program."
)
ARCHITECTURE_ONLY_FLAGS = {
    "architecture_only": True,
    "research_only": True,
    "local_only": True,
    "documents_only": True,
    "not_implemented": True,
    "no_broker_access": True,
    "no_broker_api": True,
    "no_pocket_option_login": True,
    "no_browser_automation": True,
    "no_selenium": True,
    "no_playwright": True,
    "no_authentication": True,
    "no_credentials": True,
    "no_order_placement": True,
    "no_live_trading": True,
    "no_money_handling": True,
    "no_external_execution_adapters": True,
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
UNSAFE_STATE_PHRASES = (
    "Ready For Live Trading",
    "Broker Ready",
    "Execution Ready",
)
