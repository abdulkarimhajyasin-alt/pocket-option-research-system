"""Backup and recovery design blueprint."""

from app.production_system_design.models import BackupRecoveryPlan, design_category


class BackupRecoveryBuilder:
    """Build backup and recovery design only."""

    def build(self) -> BackupRecoveryPlan:
        return design_category(
            BackupRecoveryPlan,
            "backup_recovery",
            "Backup and Recovery Design",
            [
                "Backup scope",
                "Restore tests",
                "Disaster recovery objectives",
                "RPO/RTO targets",
                "Artifact preservation",
                "Configuration recovery",
                "Audit recovery",
            ],
        )
