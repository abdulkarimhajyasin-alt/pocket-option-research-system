"""Retention policy rules for repository hygiene."""

from __future__ import annotations

from typing import Any

from app.repository_hygiene.models import RetentionRule
from app.repository_hygiene.schemas import HYGIENE_ONLY_FLAGS


class RetentionPolicyEngine:
    """Define local artifact retention rules."""

    RULES = (
        ("RET-ARCHIVE", "research archive snapshots", "retain latest five locally", True, True),
        ("RET-LATEST", "latest snapshots", "retain current latest snapshot", True, True),
        ("RET-DIFF", "diffs", "retain release-linked diffs, review older diffs", True, True),
        ("RET-RELEASE", "release reports", "retain as release evidence", True, True),
        ("RET-CERT", "certification reports", "retain as assurance evidence", True, True),
        ("RET-DASH", "dashboard reports", "retain latest generated report set", True, False),
        ("RET-DIAG", "diagnostics reports", "retain until next accepted validation", True, False),
        (
            "RET-VALID",
            "validation artifacts",
            "retain when tied to release evidence",
            True,
            False,
        ),
        (
            "RET-PHASE",
            "prompt files",
            "retain phase prompts as implementation evidence",
            True,
            True,
        ),
        ("RET-TEMP", "temporary files", "eligible for manual cleanup only", True, False),
    )

    def build(self) -> dict[str, Any]:
        return {
            "items": [
                RetentionRule(
                    rule_id=rule_id,
                    artifact_type=artifact_type,
                    retention=retention,
                    manual_review_required=manual,
                    preserve_as_release_evidence=preserve,
                ).to_dict()
                for rule_id, artifact_type, retention, manual, preserve in self.RULES
            ],
            **HYGIENE_ONLY_FLAGS,
        }
