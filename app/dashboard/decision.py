"""Deterministic Arabic research decision layer for the dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from app.dashboard.formatting import format_percent, format_relative_time, parse_datetime
from app.dashboard.models import DashboardOverview, DatasetSummary, ValidationSummary


@dataclass(frozen=True)
class ResearchDecision:
    """Arabic research conclusion with an actionable next step."""

    status: str
    severity: str
    explanation: str
    next_step: str

    def to_dict(self) -> dict[str, str]:
        return {
            "status": self.status,
            "severity": self.severity,
            "explanation": self.explanation,
            "next_step": self.next_step,
        }


@dataclass(frozen=True)
class ResearchHealthScore:
    """Unified research-readiness score, not a profitability score."""

    score: int
    label: str
    severity: str
    explanation: str

    def to_dict(self) -> dict[str, object]:
        return {
            "score": self.score,
            "label": self.label,
            "severity": self.severity,
            "explanation": self.explanation,
        }


def dataset_decision(dataset: DatasetSummary | None) -> ResearchDecision:
    """Evaluate whether a dataset is suitable for research use."""
    if dataset is None or dataset.quality_score is None:
        return ResearchDecision(
            "غير كاف للحكم",
            "warning",
            "لا توجد درجة جودة بيانات محفوظة يمكن الاعتماد عليها.",
            "شغل فحص جودة البيانات ثم أعد فتح هذه الصفحة.",
        )
    if dataset.integrity_status != "passed":
        return ResearchDecision(
            "يحتاج تنظيف",
            "warning",
            "سلامة البيانات لم تنجح بالكامل، لذلك قد تؤثر الفجوات أو التكرارات على نتائج البحث.",
            "راجع تقرير الجودة ونظف الفجوات أو التكرارات قبل التحقق.",
        )
    if dataset.quality_score >= 95 and dataset.gap_count == 0 and dataset.duplicate_count == 0:
        return ResearchDecision(
            "صالح للاختبار",
            "healthy",
            f"جودة البيانات {format_percent(dataset.quality_score)} مع سلامة مكتملة.",
            "استخدم البيانات في تحقق أوسع مع متابعة حداثة التقرير.",
        )
    if dataset.quality_score >= 80:
        return ResearchDecision(
            "يحتاج تنظيف",
            "warning",
            (
                f"جودة البيانات {format_percent(dataset.quality_score)} "
                "لكنها تحتوي على فجوات أو تكرارات."
            ),
            "نظف البيانات ثم أعد تشغيل فحص الجودة.",
        )
    return ResearchDecision(
        "مرفوض",
        "critical",
        f"جودة البيانات {format_percent(dataset.quality_score)} أقل من الحد البحثي الآمن.",
        "استبدل المصدر أو ابن نسخة بيانات أنظف قبل أي تحقق.",
    )


def validation_decision(validation: ValidationSummary | None) -> ResearchDecision:
    """Evaluate validation quality for one strategy/dataset run."""
    if validation is None or validation.robustness_score is None:
        return ResearchDecision(
            "غير كاف للحكم",
            "warning",
            "لا يوجد تقرير تحقق مكتمل بدرجة متانة قابلة للعرض.",
            "شغل مسار التحقق ثم راجع النتيجة.",
        )
    warnings = len(validation.overfitting_warnings)
    windows = int(validation.walk_forward_summary.get("windows") or 0)
    sweeps = int(validation.parameter_sweep_summary.get("results") or 0)
    if validation.robustness_score >= 70 and warnings == 0 and windows > 0 and sweeps > 0:
        return ResearchDecision(
            "صالح للمتابعة",
            "healthy",
            (
                f"المتانة {format_percent(validation.robustness_score)} "
                "مع تحقق متعدد الجوانب دون تحذيرات."
            ),
            "وسع الاختبار على بيانات أحدث ولا تعتبر ذلك وعدا بالربحية.",
        )
    if validation.robustness_score < 40 or warnings >= 3:
        return ResearchDecision(
            "مرفوض بحثيا",
            "critical",
            f"المتانة {format_percent(validation.robustness_score)} مع {warnings} تحذير.",
            "عد إلى فرضية الاستراتيجية أو معايير الفلترة قبل المزيد من الاختبارات.",
        )
    return ResearchDecision(
        "يحتاج تحسين",
        "warning",
        f"المتانة {format_percent(validation.robustness_score)} وتحتاج تغطية تحقق أوضح.",
        "نفذ اختبار Walk-forward أوسع وفحص معاملات أكثر قبل المتابعة.",
    )


def research_decision(overview: DashboardOverview) -> ResearchDecision:
    """Evaluate the overall dashboard research conclusion."""
    validation = overview.validations[0] if overview.validations else None
    dataset = overview.datasets[0] if overview.datasets else None
    dataset_result = dataset_decision(dataset)
    validation_result = validation_decision(validation)
    warning_count = sum(overview.warning_counts.values())
    if validation_result.severity == "critical" or dataset_result.severity == "critical":
        return ResearchDecision(
            "مرفوض بحثيا",
            "critical",
            "أحد مسارات البيانات أو التحقق لا يفي بالحد الأدنى للمتابعة البحثية.",
            "ابدأ بمعالجة السبب الحرج الظاهر في صفحات البيانات والتحقق.",
        )
    if (
        validation_result.severity == "healthy"
        and dataset_result.severity == "healthy"
        and warning_count == 0
    ):
        return ResearchDecision(
            "صالح للمتابعة",
            "healthy",
            "البيانات والتحقق يقدمان أساسا بحثيا واضحا للمتابعة.",
            "وسع العينة الزمنية وراقب ثبات النتائج قبل أي قرار لاحق.",
        )
    if validation is None or dataset is None:
        return ResearchDecision(
            "غير كاف للحكم",
            "warning",
            "توجد معلومات ناقصة عن البيانات أو التحقق.",
            "أكمل توليد تقارير البيانات والتحقق أولا.",
        )
    return ResearchDecision(
        "يحتاج تحسين",
        "warning",
        "النتائج قابلة للقراءة لكنها لا تكفي للمتابعة البحثية بثقة عالية.",
        "ركز على تحسين المتانة وتقليل التحذيرات ثم أعد التحقق.",
    )


def health_score(
    overview: DashboardOverview,
    now: datetime | None = None,
) -> ResearchHealthScore:
    """Calculate a 0-100 research-readiness score."""
    robustness = _score_value(overview.latest_robustness_score)
    quality = _score_value(overview.latest_dataset_quality_score)
    warning_count = sum(overview.warning_counts.values())
    validation = overview.validations[0] if overview.validations else None
    coverage = _validation_coverage(validation)
    freshness = _freshness_score(
        overview.reports[0].modified_at if overview.reports else None,
        now,
    )
    penalty = min(25, warning_count * 6)
    score = round(
        (robustness * 0.35)
        + (quality * 0.25)
        + (coverage * 0.25)
        + (freshness * 0.15)
        - penalty
    )
    score = max(0, min(100, score))
    label, severity = _score_label(score, bool(overview.validations and overview.datasets))
    explanation = (
        "درجة جاهزية بحثية تجمع المتانة وجودة البيانات وتغطية التحقق وحداثة التقرير، "
        "ولا تمثل ربحية أو توصية تداول."
    )
    return ResearchHealthScore(score, label, severity, explanation)


def executive_summary(overview: DashboardOverview) -> dict[str, Any]:
    """Return the compact five-second overview panel payload."""
    decision = research_decision(overview)
    health = health_score(overview)
    latest_report = overview.reports[0].modified_at if overview.reports else None
    return {
        "state": decision.status,
        "decision": decision.to_dict(),
        "health": health.to_dict(),
        "reason": decision.explanation,
        "next_step": decision.next_step,
        "freshness": format_relative_time(latest_report),
    }


def strategy_decision(signal_summary: dict[str, Any] | None) -> ResearchDecision:
    """Build a strategy-level decision from latest signal research output."""
    if not signal_summary:
        return ResearchDecision(
            "غير كاف للحكم",
            "warning",
            "لا توجد نتائج بحث محفوظة لهذه الاستراتيجية بعد.",
            "شغل بحث الاستراتيجية لتوليد ملخص إشارات أولي.",
        )
    total = int(signal_summary.get("generated_signals") or signal_summary.get("total_signals") or 0)
    average_confidence = _average_confidence(signal_summary)
    if total == 0:
        return ResearchDecision(
            "يحتاج تحسين",
            "warning",
            "لم تنتج الاستراتيجية إشارات قابلة للمراجعة في آخر تشغيل.",
            "راجع شروط الدخول والفلاتر ثم أعد تشغيل البحث.",
        )
    if average_confidence >= 0.65:
        return ResearchDecision(
            "صالح للمتابعة",
            "healthy",
            f"آخر تشغيل أنتج {total} إشارات مع متوسط ثقة جيد.",
            "انقل النتيجة إلى تحقق بيانات أوسع.",
        )
    return ResearchDecision(
        "يحتاج تحسين",
        "warning",
        f"آخر تشغيل أنتج {total} إشارات لكن الثقة المتوسطة ما زالت محدودة.",
        "راجع مصادر الأدلة التي تخفض الثقة.",
    )


def _score_value(value: float | None) -> float:
    return 0.0 if value is None else max(0.0, min(100.0, float(value)))


def _validation_coverage(validation: ValidationSummary | None) -> float:
    if validation is None:
        return 0.0
    windows = int(validation.walk_forward_summary.get("windows") or 0)
    sweeps = int(validation.parameter_sweep_summary.get("results") or 0)
    out_sample = 1 if validation.out_of_sample_summary else 0
    return min(100.0, (min(windows, 5) * 12) + (min(sweeps, 10) * 3) + (out_sample * 25))


def _freshness_score(value: Any, now: datetime | None) -> float:
    parsed = parse_datetime(value)
    if parsed is None:
        return 0.0
    reference = now or datetime.now(parsed.tzinfo)
    age = reference - parsed
    if age <= timedelta(days=1):
        return 100.0
    if age <= timedelta(days=7):
        return 80.0
    if age <= timedelta(days=30):
        return 55.0
    return 30.0


def _score_label(score: int, enough_data: bool) -> tuple[str, str]:
    if not enough_data:
        return "غير كاف", "warning"
    if score >= 85:
        return "ممتاز", "healthy"
    if score >= 70:
        return "جيد", "healthy"
    if score >= 50:
        return "متوسط", "warning"
    return "ضعيف", "critical"


def _average_confidence(signal_summary: dict[str, Any]) -> float:
    values = signal_summary.get("average_confidence_by_evidence", {})
    if not isinstance(values, dict) or not values:
        return 0.0
    numeric = [float(value) for value in values.values() if isinstance(value, (int, float))]
    return sum(numeric) / len(numeric) if numeric else 0.0
