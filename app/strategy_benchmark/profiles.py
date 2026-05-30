"""Default benchmark profiles."""

from __future__ import annotations

from app.strategy_benchmark.models import BenchmarkProfile


def default_benchmark_profiles() -> tuple[BenchmarkProfile, ...]:
    """Return deterministic research benchmark profiles."""
    base_weights = {
        "readiness": 0.18,
        "stability": 0.16,
        "consistency": 0.14,
        "confidence": 0.14,
        "signal": 0.14,
        "opportunity": 0.12,
        "confluence": 0.12,
    }
    return (
        BenchmarkProfile(
            "current",
            "الملف الحالي",
            "خط الأساس الحالي للمقارنة البحثية.",
            base_weights,
            {"minimum_score": 60, "minimum_stability": 55},
        ),
        BenchmarkProfile(
            "conservative",
            "الملف المحافظ",
            "يرفع وزن الاستقرار والتكرارية ويخفض حساسية الفرص.",
            {**base_weights, "stability": 0.22, "opportunity": 0.08},
            {"minimum_score": 70, "minimum_stability": 70},
        ),
        BenchmarkProfile(
            "balanced",
            "الملف المتوازن",
            "يوزع الوزن بين الجاهزية والجودة والاستقرار.",
            {**base_weights, "readiness": 0.2, "signal": 0.15},
            {"minimum_score": 65, "minimum_stability": 60},
        ),
        BenchmarkProfile(
            "aggressive",
            "الملف النشط",
            "يرفع وزن جودة الفرص والتوافق مع قبول تذبذب أعلى.",
            {**base_weights, "opportunity": 0.18, "confluence": 0.16, "stability": 0.1},
            {"minimum_score": 62, "minimum_stability": 50},
        ),
        BenchmarkProfile(
            "experimental",
            "الملف التجريبي",
            "يستخدم للمقارنة البحثية فقط عند اختبار فرضيات جديدة.",
            {**base_weights, "confidence": 0.2, "consistency": 0.1},
            {"minimum_score": 55, "minimum_stability": 45},
            {"experimental": True},
        ),
    )
