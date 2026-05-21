import frappe
from frappe.model.document import Document

from zkteco_biometric_integration.zkteco_biometric_integration import (
	SCHEDULED_JOB_METHOD,
)


def execute():
	update_scheduled_job()


def get_current_frequency_settings() -> "Document":
	return frappe.get_doc("ZKTeco Global")


def update_scheduled_job() -> None:
	setting_doc = get_current_frequency_settings()

	new_frequency = setting_doc.cron_expression if setting_doc.is_cron else setting_doc.fetch_frequency

	if job_doc_name := frappe.db.exists("Scheduled Job Type", {"method": SCHEDULED_JOB_METHOD}):
		job_doc = frappe.get_doc("Scheduled Job Type", job_doc_name)
		if setting_doc.fetch_frequency == job_doc.frequency:
			return
		job_doc.db_set(
			{"cron_format": setting_doc.cron_expression, "frequency": new_frequency},
			update_modified=False,
		)
