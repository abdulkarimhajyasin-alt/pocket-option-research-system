"""Schema constants for repository hygiene outputs."""

SCHEMA_VERSION = "repository_hygiene.v1"

HYGIENE_ONLY_FLAGS = {
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

SAFE_CLEANUP_ACTIONS = (
    "keep",
    "review manually",
    "add to ignore recommendation",
    "archive externally",
    "eligible for manual cleanup",
    "do not delete automatically",
)

SAFETY_LEVELS = (
    "آمن",
    "يحتاج مراجعة",
    "حساس",
    "ممنوع تلقائياً",
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
)
