import frappe
from frappe.model.document import Document

from zkteco_biometric_integration.zkteco_biometric_integration import (
	SCHEDULED_JOB_METHOD,
)
from zkteco_biometric_integration.zkteco_biometric_integration.doctype.zkteco_global.zkteco_global import (
	ZKTecoGlobal,
)


def execute():
	update_scheduled_job()


def get_current_frequency_settings() -> ZKTecoGlobal:
	return frappe.get_doc("ZKTeco Global")


def update_scheduled_job() -> None:
	setting_doc = get_current_frequency_settings()

	new_frequency = setting_doc.cron_expression if setting_doc.is_cron else setting_doc.fetch_frequency

	if job_doc_name := frappe.db.exists("Scheduled Job Type", {"method": SCHEDULED_JOB_METHOD}):
		job_doc = frappe.get_doc("Scheduled Job Type", job_doc_name)
		if setting_doc.fetch_frequency == job_doc.frequency:
			return
		data = {"frequency": new_frequency}
		if setting_doc.is_cron:
			data["cron_expression"] = setting_doc.cron_expression
		job_doc.db_set(data, update_modified=False)
