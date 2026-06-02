"""Schema constants for release baseline reconciliation outputs."""

SCHEMA_VERSION = "release_baseline.v1"

BASELINE_ONLY_FLAGS = {
    "baseline_reconciliation_only": True,
    "manual_cleanup_planning_only": True,
    "repository_hygiene_only": True,
    "artifact_policy_only": True,
    "governance_only": True,
    "design_only": True,
    "architecture_only": True,
    "research_only": True,
    "local_only": True,
    "non_destructive": True,
    "no_automatic_file_deletion": True,
    "no_destructive_git_commands": True,
    "no_gitignore_modification": True,
    "no_broker_access": True,
    "no_execution_capability": True,
    "no_trading_capability": True,
    "no_authentication": True,
    "no_credentials": True,
    "no_browser_automation": True,
    "no_money_handling": True,
    "no_external_connectivity": True,
    "no_real_operational_control": True,
}

ALLOWED_BASELINE_STATES = (
    "Not Ready",
    "Needs Manual Review",
    "Ready For Baseline Commit Review",
)

FORBIDDEN_BASELINE_STATES = (
    "Ready For Live Trading",
    "Ready For Execution",
    "Broker Ready",
    "Production Trading Approved",
    "Approved For Real Trading",
)

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
    "git " + "clean",
    "git " + "reset",
    "git " + "checkout",
)
