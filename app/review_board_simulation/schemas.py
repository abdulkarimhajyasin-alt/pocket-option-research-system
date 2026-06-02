"""Schema constants for review board simulation outputs."""

SCHEMA_VERSION = "review_board_simulation.v1"

ALLOWED_DECISION_STATES = (
    "Simulated Pass",
    "Simulated Conditional Pass",
    "Simulated Blocked",
    "Simulated Not Ready",
    "Requires Human Review",
)

FORBIDDEN_DECISION_STATES = (
    "Approved For Live Trading",
    "Ready For Live Trading",
    "Ready For Execution",
    "Broker Ready",
    "Production Trading Approved",
    "Approved For Real Trading",
    "Operationally Approved For Trading",
)

SIMULATION_ONLY_FLAGS = {
    "simulation_only": True,
    "review_only": True,
    "dry_run_only": True,
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
    "no_real_approvals": True,
    "no_real_users": True,
    "no_real_permissions": True,
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
    "requests" + ".",
    "urllib" + ".",
    "httpx" + ".",
)
