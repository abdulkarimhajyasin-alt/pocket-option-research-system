"""Safe allowlisted research actions for the dashboard."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from loguru import logger

from app.dashboard.models import ActionDefinition, ActionResult
from app.jobs.models import JobResult
from app.jobs.registry import JobRegistry


ACTION_DEFINITIONS: dict[str, ActionDefinition] = {
    "strategy_research": ActionDefinition(
        name="strategy_research",
        label="تشغيل بحث الاستراتيجية",
        description="تشغيل مسار بحث الاستراتيجية القابل للتفسير.",
        command=("scripts/run_strategy_research.py",),
    ),
    "validation": ActionDefinition(
        name="validation",
        label="تشغيل التحقق",
        description="تشغيل مسار التحقق الكامل.",
        command=("scripts/run_validation.py",),
    ),
    "walk_forward": ActionDefinition(
        name="walk_forward",
        label="تحقق النافذة المتحركة",
        description="تشغيل تحقق النافذة المتحركة فقط.",
        command=("scripts/run_walk_forward.py",),
    ),
    "parameter_sweep": ActionDefinition(
        name="parameter_sweep",
        label="فحص المعاملات",
        description="تشغيل فحص المعاملات المسموح به.",
        command=("scripts/run_parameter_sweep.py",),
    ),
    "research_report": ActionDefinition(
        name="research_report",
        label="توليد تقرير البحث",
        description="توليد تقارير بحث الاستراتيجية.",
        command=("scripts/run_research_report.py",),
    ),
    "dataset_quality": ActionDefinition(
        name="dataset_quality",
        label="فحص جودة البيانات",
        description="تحليل جودة البيانات وتوليد التقارير.",
        command=("scripts/check_dataset_quality.py",),
    ),
    "dataset_statistics": ActionDefinition(
        name="dataset_statistics",
        label="إحصاءات البيانات",
        description="توليد إحصاءات مجموعة البيانات.",
        command=("scripts/run_dataset_statistics.py",),
    ),
    "dataset_comparison": ActionDefinition(
        name="dataset_comparison",
        label="مقارنة البيانات",
        description="مقارنة مجموعات البيانات البحثية المسجلة.",
        command=("scripts/run_dataset_comparison.py",),
    ),
    "dataset_integrity": ActionDefinition(
        name="dataset_integrity",
        label="تحقق سلامة البيانات",
        description="التحقق من مخطط البيانات والبصمة والمجموع الاختباري.",
        command=("scripts/verify_dataset_integrity.py",),
    ),
    "execution_simulation": ActionDefinition(
        name="execution_simulation",
        label="تشغيل محاكاة التنفيذ",
        description="تشغيل مختبر تنفيذ محلي على بيانات تاريخية فقط دون أي اتصال خارجي.",
        command=("scripts/run_execution_simulation.py",),
    ),
    "observation_layer": ActionDefinition(
        name="observation_layer",
        label="تشغيل مراقبة السوق",
        description="جمع ملاحظات سوق محلية وهمية للبحث فقط دون اتصال وسيط أو تنفيذ.",
        command=("scripts/run_observation_layer.py",),
    ),
    "live_feed": ActionDefinition(
        name="live_feed",
        label="تشغيل البث المباشر",
        description="تشغيل خط بث سوق وهمي للمراقبة والبحث فقط دون اتصال وسيط أو تنفيذ.",
        command=("scripts/run_live_feed.py",),
    ),
    "market_data": ActionDefinition(
        name="market_data",
        label="تحديث بيانات السوق",
        description="تشغيل تكامل بيانات سوق بحثي فقط دون تنفيذ أو تحكم وسيط.",
        command=("scripts/run_market_data.py",),
    ),
    "signal_intelligence": ActionDefinition(
        name="signal_intelligence",
        label="تحديث ذكاء الإشارات",
        description="تشغيل تصنيف إشارات بحثي فقط دون تنفيذ أو توصيات استثمارية.",
        command=("scripts/run_signal_intelligence.py",),
    ),
    "signal_performance": ActionDefinition(
        name="signal_performance",
        label="تحديث أداء الإشارات",
        description="تشغيل تقييم أداء الإشارات بحثيا فقط دون تنفيذ أو إدارة أموال.",
        command=("scripts/run_signal_performance.py",),
    ),
    "opportunity_engine": ActionDefinition(
        name="opportunity_engine",
        label="تحديث الفرص المؤهلة",
        description="تشغيل تأهيل وترتيب الفرص بحثيا فقط دون توصيات أو تنفيذ.",
        command=("scripts/run_opportunity_engine.py",),
    ),
    "multi_timeframe": ActionDefinition(
        name="multi_timeframe",
        label="تحديث تأكيد الأطر الزمنية",
        description="تشغيل تأكيد متعدد الأطر الزمنية بحثيا فقط دون توصيات أو تنفيذ.",
        command=("scripts/run_multi_timeframe.py",),
    ),
    "confluence": ActionDefinition(
        name="confluence",
        label="تحديث محرك التوافق",
        description="تشغيل التوافق البحثي الموحد دون توصيات أو تنفيذ.",
        command=("scripts/run_confluence.py",),
    ),
    "trade_lifecycle": ActionDefinition(
        name="trade_lifecycle",
        label="تحديث دورة حياة الفرص",
        description="تشغيل محاكاة دورة الحياة بحثيا فقط دون تنفيذ أو أوامر.",
        command=("scripts/run_trade_lifecycle.py",),
    ),
    "strategy_readiness": ActionDefinition(
        name="strategy_readiness",
        label="تحديث جاهزية الاستراتيجية",
        description="تشغيل تقييم الجاهزية البحثية دون موافقة نشر أو تنفيذ.",
        command=("scripts/run_strategy_readiness.py",),
    ),
    "strategy_benchmark": ActionDefinition(
        name="strategy_benchmark",
        label="تحديث مقارنة الاستراتيجيات",
        description="تشغيل مقارنة الملفات البحثية دون تنفيذ أو توصيات تداول.",
        command=("scripts/run_strategy_benchmark.py",),
    ),
    "pattern_memory": ActionDefinition(
        name="pattern_memory",
        label="تحديث ذاكرة الأنماط",
        description="تشغيل محرك التعلم والأنماط للبحث فقط دون تنفيذ أو أتمتة.",
        command=("scripts/run_pattern_memory.py",),
    ),
    "market_regime": ActionDefinition(
        name="market_regime",
        label="تحديث حالة السوق",
        description="تشغيل محرك حالة السوق للبحث فقط دون اتصال وسيط أو تنفيذ.",
        command=("scripts/run_market_regime.py",),
    ),
    "research_certification": ActionDefinition(
        name="research_certification",
        label="تحديث الاعتماد البحثي",
        description="تشغيل قرار الاعتماد البحثي دون نشر أو تداول أو تنفيذ.",
        command=("scripts/run_research_certification.py",),
    ),
    "observation_readiness": ActionDefinition(
        name="observation_readiness",
        label="تحديث جاهزية المراقبة",
        description="تشغيل جاهزية المراقبة السلبية دون تنفيذ أو تحكم وسيط.",
        command=("scripts/run_broker_readiness.py",),
    ),
    "external_observation": ActionDefinition(
        name="external_observation",
        label="تحديث بيئة المراقبة الخارجية",
        description="تشغيل صندوق مراقبة خارجي سلبي دون اتصال أو مصادقة أو تنفيذ.",
        command=("scripts/run_external_observation.py",),
    ),
    "browser_observation": ActionDefinition(
        name="browser_observation",
        label="تحديث مراقبة المتصفح",
        description="تحليل لقطات متصفح موجودة للقراءة فقط دون فتح متصفح أو مصادقة.",
        command=("scripts/run_browser_observation.py",),
    ),
    "snapshot_import": ActionDefinition(
        name="snapshot_import",
        label="تحديث استيراد اللقطات",
        description="تحليل الملفات التي تم رفعها يدويا فقط دون جلب أو اتصال خارجي.",
        command=("scripts/run_snapshot_import.py",),
    ),
    "observation_intelligence": ActionDefinition(
        name="observation_intelligence",
        label="تحديث ذكاء المراقبة",
        description="توحيد مخرجات المراقبة المحلية في نموذج بحثي واحد دون تنفيذ.",
        command=("scripts/run_observation_intelligence.py",),
    ),
    "market_observation": ActionDefinition(
        name="market_observation",
        label="تحديث مصدر مراقبة السوق",
        description=(
            "إنشاء مصدر مراقبة سوق موحد من المخرجات السلبية المحلية دون تنفيذ أو أوامر "
            "أو تسجيل دخول."
        ),
        command=("scripts/run_market_observation.py",),
    ),
    "live_observation": ActionDefinition(
        name="live_observation",
        label="إعادة تشغيل المراقبة",
        description=(
            "تشغيل محاكاة تدفق الملاحظات السلبية محليا دون تنفيذ أو وسيط أو أتمتة."
        ),
        command=("scripts/run_live_observation.py",),
    ),
    "signal_stream": ActionDefinition(
        name="signal_stream",
        label="تدفق الإشارات",
        description="توليد تدفق إشارات بحثي من الملاحظات المعاد تشغيلها دون تنفيذ.",
        command=("scripts/run_signal_stream.py",),
    ),
    "execution_readiness": ActionDefinition(
        name="execution_readiness",
        label="جاهزية التنفيذ",
        description=(
            "تقييم جاهزية الإشارات البحثية لطبقة ورقية مستقبلية دون تنفيذ أو أوامر أو وسيط."
        ),
        command=("scripts/run_execution_readiness.py",),
    ),
    "research_operations": ActionDefinition(
        name="research_operations",
        label="تحديث مركز العمليات البحثية",
        description="تشغيل ملخص العمليات البحثية دون تنفيذ أو توصيات تداول.",
        command=("scripts/run_research_ops.py",),
    ),
}


class DashboardActionRunner:
    """Execute only fixed safe research actions."""

    def __init__(self, project_root: Path | str = ".", timeout_seconds: int = 120) -> None:
        self.project_root = Path(project_root)
        self.timeout_seconds = timeout_seconds

    def list_actions(self) -> list[ActionDefinition]:
        """Return allowlisted dashboard actions."""
        return list(ACTION_DEFINITIONS.values())

    def run(self, action_name: str) -> ActionResult:
        """Execute one allowlisted action with no shell interpolation."""
        job_result = self.run_job(action_name)
        action = ACTION_DEFINITIONS[action_name]
        return ActionResult(
            action_name=action.name,
            label=action.label,
            exit_code=job_result.exit_code,
            stdout=job_result.stdout,
            stderr=job_result.stderr,
            command_display="python " + " ".join(action.command),
            timed_out=job_result.exit_code == 124,
            error=job_result.error,
        )

    def run_job(self, action_name: str) -> JobResult:
        """Execute one allowlisted action and return a background-job result."""
        if action_name not in ACTION_DEFINITIONS:
            logger.bind(component="dashboard").warning(
                "Invalid dashboard action requested: {}",
                action_name,
            )
            raise KeyError(f"Unknown dashboard action: {action_name}")
        action = ACTION_DEFINITIONS[action_name]
        command = (sys.executable, *action.command)
        logger.bind(component="dashboard").info("Running dashboard action {}", action.name)
        try:
            completed = subprocess.run(
                command,
                cwd=self.project_root,
                check=False,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            if completed.returncode != 0:
                logger.bind(component="dashboard").warning(
                    "Dashboard action {} failed with exit code {}",
                    action.name,
                    completed.returncode,
                )
            return JobResult(
                exit_code=completed.returncode,
                stdout=self._trim(completed.stdout),
                stderr=self._trim(completed.stderr),
            )
        except subprocess.TimeoutExpired as exc:
            logger.bind(component="dashboard").warning(
                "Dashboard action {} timed out",
                action.name,
            )
            return JobResult(
                exit_code=124,
                stdout=self._trim(exc.stdout or ""),
                stderr=self._trim(exc.stderr or ""),
                error="Action timed out",
            )

    def _trim(self, value: str, limit: int = 6000) -> str:
        if len(value) <= limit:
            return value
        return value[-limit:]

    def job_registry(self) -> JobRegistry:
        """Return a job registry backed by this runner."""
        registry = JobRegistry()
        for action in ACTION_DEFINITIONS.values():
            registry.register(action, lambda name=action.name: self.run_job(name))
        return registry
