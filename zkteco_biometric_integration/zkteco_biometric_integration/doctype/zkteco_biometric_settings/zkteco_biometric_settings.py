# Copyright (c) 2025, Navari Limited and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe.model.document import Document


class ZKTecoBiometricSettings(Document):
	def before_insert(self):
		self.token = self.generate_token()
		frappe.msgprint("Token generated succesfully")

	def before_save(self):
		self.manage_checkin_scheduler()

	def generate_token(self, doctype=None):
		headers = {"Content-Type": "application/json"}

		self.url_path = "/jwt-api-token-auth/"
		endpoint_url = f"{self.url}{self.url_path}"

		if doctype:
			doc = frappe.get_doc(doctype, self.username)
			password = doc.get_password("password")
		else:
			password = self.password

		payload = {"username": self.username, "password": password}

		try:
			response = requests.post(endpoint_url, payload, headers)

			if response.status_code == 200:
				return response.json().get("token")
			else:
				frappe.throw(f"Problem generating Token: {response.json().get("detail")}")

		except Exception as e:
			frappe.throw("Problem generating Token", str(e))


def manage_checkin_scheduler(self):
	method = "zkteco_biometric_integration.zkteco_biometric_integration.controller.zkteco_transactions_sync.handle_employee_checkin"

	exists = frappe.db.exists("Scheduled Job Type", {"method": method})

	if self.enable:
		if not exists:
			scheduled_job = frappe.get_doc(
				{
					"doctype": "Scheduled Job Type",
					"method": method,
					"frequency": self.fetch_frequency,
					"stopped": 0,
					"cron_format": self.cron_expression if self.fetch_frequency == "Cron" else None,
				}
			)
			scheduled_job.insert()

		frappe.db.set_value(
			"Scheduled Job Type",
			{"method": method},
			{
				"stopped": 0,
				"frequency": self.fetch_frequency,
				"cron_format": self.cron_expression if self.fetch_frequency == "Cron" else None,
			},
		)

	else:
		if exists:
			frappe.db.set_value("Scheduled Job Type", {"method": method}, "stopped", 1)
			frappe.delete_doc("Scheduled Job Type", exists)
