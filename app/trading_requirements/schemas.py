"""Schema constants for trading requirements outputs."""

SCHEMA_VERSION = "trading_requirements.v1"
SAFE_DECISION_STATES = (
    "Not Ready",
    "Requirements Incomplete",
    "Ready For Architecture Review",
)
FORBIDDEN_DECISION_STATES = (
    "Ready For Live Trading",
    "Ready For Execution",
    "Broker Ready",
    "Approved For Real Trading",
)
REQUIREMENTS_ONLY_FLAGS = {
    "requirements_only": True,
    "architecture_only": True,
    "research_only": True,
    "local_only": True,
    "not_implemented": True,
    "no_broker_access": True,
    "no_execution_capability": True,
    "no_trading_capability": True,
    "no_authentication": True,
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
