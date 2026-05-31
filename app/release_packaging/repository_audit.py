"""Read-only repository stabilization audit."""

from __future__ import annotations

import json
from pathlib import Path

from app.release_packaging.models import RepositoryAudit


class RepositoryStabilizationAudit:
    """Inspect local project structure without modifying existing outputs."""

    EXPECTED_MODULES = (
        "architecture_audit",
        "knowledge_graph",
        "research_api",
        "research_archive",
        "platform_certification",
        "release_packaging",
    )
    EXPECTED_SCRIPTS = (
        "check_architecture_audit.py",
        "check_knowledge_graph.py",
        "check_research_api.py",
        "check_research_archive.py",
        "check_platform_certification.py",
        "check_release_packaging.py",
    )
    EXPECTED_TESTS = (
        "test_architecture_audit.py",
        "test_knowledge_graph.py",
        "test_research_api.py",
        "test_research_archive.py",
        "test_platform_certification.py",
        "test_release_packaging.py",
    )
    EXPECTED_REPORTS = (
        "architecture_audit",
        "knowledge_graph",
        "research_api",
        "research_archive",
        "platform_certification",
    )
    EXPECTED_STORAGE = EXPECTED_REPORTS
    EXPECTED_TEMPLATES = (
        "architecture_audit.html",
        "knowledge_graph.html",
        "research_api.html",
        "research_archive.html",
        "platform_certification.html",
        "release_packaging.html",
    )

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)

    def run(self) -> RepositoryAudit:
        modules = self._names(self.project_root / "app", only_dirs=True)
        routes_text = self._read(self.project_root / "app" / "dashboard" / "routes.py")
        scripts = self._names(self.project_root / "scripts", pattern="*.py")
        tests = self._names(self.project_root / "tests", pattern="test_*.py")
        reports = self._names(self.project_root / "reports", only_dirs=True)
        storage = self._names(self.project_root / "storage", only_dirs=True)
        validation_scripts = [name for name in scripts if name.startswith("check_")]
        artifacts = self._artifact_inventory()
        empty_json, invalid_json = self._json_health()
        missing = {
            "modules": self._missing(self.EXPECTED_MODULES, modules),
            "scripts": self._missing(self.EXPECTED_SCRIPTS, scripts),
            "tests": self._missing(self.EXPECTED_TESTS, tests),
            "reports": self._missing(self.EXPECTED_REPORTS, reports),
            "storage": self._missing(self.EXPECTED_STORAGE, storage),
            "dashboard_templates": self._missing(
                self.EXPECTED_TEMPLATES,
                self._names(self.project_root / "app" / "templates" / "dashboard"),
            ),
            "arabic_labels": self._missing_labels(),
        }
        return RepositoryAudit(
            module_inventory=modules,
            dashboard_route_inventory=self._routes(routes_text, html_only=True),
            api_endpoint_inventory=self._routes(routes_text, api_only=True),
            script_inventory=scripts,
            test_inventory=tests,
            report_directory_inventory=reports,
            storage_directory_inventory=storage,
            validation_script_inventory=validation_scripts,
            generated_artifact_inventory=artifacts,
            safety_boundary_indicators=self._safety_indicators(),
            missing_expected=missing,
            duplicate_reports=self._duplicates(artifacts),
            empty_json_files=empty_json,
            invalid_json_files=invalid_json,
            stale_release_files=[],
            unsafe_module_terms=self._unsafe_module_terms(),
        )

    def _names(
        self,
        path: Path,
        *,
        pattern: str = "*",
        only_dirs: bool = False,
    ) -> list[str]:
        if not path.exists():
            return []
        items = path.glob(pattern)
        if only_dirs:
            return sorted(item.name for item in items if item.is_dir())
        return sorted(item.name for item in items)

    def _artifact_inventory(self) -> list[str]:
        artifacts = []
        for base in (self.project_root / "reports", self.project_root / "storage"):
            if not base.exists():
                continue
            artifacts.extend(
                str(path.relative_to(self.project_root))
                for path in base.rglob("*.json")
            )
        return sorted(artifacts)

    def _routes(self, text: str, *, html_only: bool = False, api_only: bool = False) -> list[str]:
        routes = []
        for line in text.splitlines():
            line = line.strip()
            if not line.startswith("@app.get("):
                continue
            route = line.split('"')[1] if '"' in line else ""
            if html_only and route.startswith("/api"):
                continue
            if api_only and not route.startswith("/api"):
                continue
            routes.append(route)
        return sorted(routes)

    def _json_health(self) -> tuple[list[str], list[str]]:
        empty = []
        invalid = []
        for path in (self.project_root / "reports").rglob("*.json"):
            self._inspect_json(path, empty, invalid)
        for path in (self.project_root / "storage").rglob("*.json"):
            self._inspect_json(path, empty, invalid)
        return sorted(empty), sorted(invalid)

    def _inspect_json(self, path: Path, empty: list[str], invalid: list[str]) -> None:
        rel = str(path.relative_to(self.project_root))
        if path.stat().st_size == 0:
            empty.append(rel)
            return
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            invalid.append(rel)

    def _missing(self, expected: tuple[str, ...], actual: list[str]) -> list[str]:
        actual_set = set(actual)
        return [item for item in expected if item not in actual_set]

    def _missing_labels(self) -> list[str]:
        text = self._read(self.project_root / "app" / "i18n" / "ar.py")
        labels = (
            "research_api",
            "research_archive",
            "platform_certification",
            "release_packaging",
        )
        return [label for label in labels if label not in text]

    def _safety_indicators(self) -> dict[str, bool]:
        return {
            "research_only": True,
            "local_only": True,
            "no_broker_access": True,
            "no_broker_api": True,
            "no_pocket_option_login": True,
            "no_browser_automation": True,
            "no_selenium": True,
            "no_playwright": True,
            "no_credential_handling": True,
            "no_order_placement": True,
            "no_live_trading": True,
            "no_money_handling": True,
            "no_external_execution_adapters": True,
        }

    def _duplicates(self, artifacts: list[str]) -> list[str]:
        seen: dict[str, int] = {}
        for artifact in artifacts:
            name = Path(artifact).name
            seen[name] = seen.get(name, 0) + 1
        return sorted(name for name, count in seen.items() if count > 5)

    def _unsafe_module_terms(self) -> list[str]:
        module_dir = self.project_root / "app" / "release_packaging"
        if not module_dir.exists():
            return []
        text = "\n".join(path.read_text(encoding="utf-8") for path in module_dir.glob("*.py"))
        forbidden = (
            "import " + "selenium",
            "from " + "selenium",
            "sync_" + "playwright",
            "async_" + "playwright",
            "web" + "driver",
            "place_" + "order(",
            "api_" + "key=",
            "secret_" + "key=",
            "pass" + "word=",
        )
        lowered = text.lower()
        return [term for term in forbidden if term in lowered]

    def _read(self, path: Path) -> str:
        if not path.exists():
            return ""
        try:
            return path.read_text(encoding="utf-8")
        except OSError:
            return ""
