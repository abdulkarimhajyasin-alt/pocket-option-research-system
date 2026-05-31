"""Replay state engine."""

from __future__ import annotations

from app.live_observation.models import ReplayResult
from app.live_observation.models import ReplayStateResult


class ReplayStateEngine:
    """Resolve Arabic replay state."""

    def evaluate(self, replay: ReplayResult) -> ReplayStateResult:
        if replay.event_count == 0:
            return ReplayStateResult("يحتاج مراجعة", 40.0, "لا توجد ملاحظات كافية للتشغيل.")
        if replay.state == "متوقف":
            return ReplayStateResult("متوقف", 60.0, "تم إيقاف إعادة التشغيل مؤقتا.")
        if replay.state == "يعمل":
            return ReplayStateResult("يعمل", 80.0, "إعادة التشغيل قيد المحاكاة.")
        if replay.state == "مكتمل":
            return ReplayStateResult("مكتمل", 100.0, "اكتملت إعادة التشغيل البحثية.")
        return ReplayStateResult("جاهز", 75.0, "المحرك جاهز لإعادة التشغيل.")
