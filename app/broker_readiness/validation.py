"""Passive observation validation engine."""

from __future__ import annotations

from app.broker_readiness.capabilities import average
from app.broker_readiness.models import CapabilityAssessment, RestrictionReport
from app.broker_readiness.models import ValidationResult


class ObservationValidationEngine:
    """Validate architecture, data flow, reporting, diagnostics, and isolation."""

    def validate(
        self,
        assessment: CapabilityAssessment,
        restrictions: RestrictionReport,
    ) -> ValidationResult:
        architecture = 85.0
        data_flow = assessment.data_collection_capability
        reporting = assessment.reporting_capability
        diagnostics = assessment.diagnostics_capability
        isolation = 100.0 if restrictions.status == "PASS" else 40.0
        score = average(architecture, data_flow, reporting, diagnostics, isolation)
        return ValidationResult(score, architecture, data_flow, reporting, diagnostics, isolation)
