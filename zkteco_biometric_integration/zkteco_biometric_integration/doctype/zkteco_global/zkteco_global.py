# Copyright (c) 2026, Navari Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from zkteco_biometric_integration.zkteco_biometric_integration import (
    SCHEDULED_JOB_METHOD,
)


class ZKTecoGlobal(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        cron_expression: DF.Data | None
        fetch_frequency: DF.Literal[
            "All",
            "Hourly",
            "Hourly Long",
            "Hourly Maintenance",
            "Daily",
            "Daily Long",
            "Daily Maintenance",
            "Weekly",
            "Weekly Long",
            "Monthly",
            "Monthly Long",
            "Yearly",
            "Cron",
        ]
    # end: auto-generated types

    def validate(self):
        self.update_schedule_job()

    @property
    def is_cron(self) -> bool:
        return self.fetch_frequency == "Cron"

    def update_schedule_job(self) -> None:

        frequency = self.cron_expression if self.is_cron else self.fetch_frequency

        if job := frappe.db.exists(
            "Scheduled Job Type", {"method": SCHEDULED_JOB_METHOD}
        ):
            job_doc = frappe.get_doc("Scheduled Job Type", job)
            job_doc.db_set(
                {"cron_format": self.cron_expression, "frequency": frequency},
                update_modified=False,
            )
