"""Schema constants for governance traceability outputs."""

SCHEMA_VERSION = "governance_traceability.v1"

SAFE_READINESS_STATES = (
    "Not Ready",
    "Traceability Incomplete",
    "Ready For Governance Review",
)

FORBIDDEN_READINESS_STATES = (
    "Ready For Live Trading",
    "Ready For Execution",
    "Broker Ready",
    "Production Trading Approved",
    "Approved For Real Trading",
    "Operationally Approved For Trading",
)

TRACEABILITY_ONLY_FLAGS = {
    "traceability_only": True,
    "governance_only": True,
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
    "no_real_operational_control": True,
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
    "execute_" + "trade(",
    "api_" + "key=",
    "secret_" + "key=",
    "pass" + "word=",
    "log" + "in(",
)
