"""Schema constants for production system design outputs."""

SCHEMA_VERSION = "production_system_design.v1"
SAFE_READINESS_STATES = (
    "Not Ready",
    "Design Incomplete",
    "Ready For Design Review",
)
FORBIDDEN_READINESS_STATES = (
    "Ready For Live Trading",
    "Ready For Execution",
    "Broker Ready",
    "Production Trading Approved",
    "Approved For Real Trading",
)
DESIGN_ONLY_FLAGS = {
    "design_only": True,
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
    "no_real_production_deployment": True,
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
