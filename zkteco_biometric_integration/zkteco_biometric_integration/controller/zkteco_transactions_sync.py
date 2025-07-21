import time

import frappe
import jwt
import requests

from zkteco_biometric_integration.zkteco_biometric_integration.doctype.zkteco_biometric_settings.zkteco_biometric_settings import (
	ZKTecoBiometricSettings,
)


@frappe.whitelist(allow_guest=True)
def get_transactions(username):
	token, url = get_configs(username)

	headers = {"Content-Type": "application/json", "Authorization": f"JWT {token}"}

	url_path = "/iclock/api/transactions/"

	endpoint_url = f"{url}{url_path}"

	try:
		response = requests.get(endpoint_url, headers=headers)
		if response.status_code == 200:
			return response.json().get("data")
		else:
			frappe.throw(f"Problem generating transactions: {response.json().get("detail")}")

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), str(e))
		frappe.throw("Problem generating transactions", str(e))


def get_configs(username):
	settings_doctype = "ZKTeco Biometric Settings"
	token, url = frappe.db.get_value(settings_doctype, username, ["token", "url"])

	token_payload = jwt.decode(token, options={"verify_signature": False})

	if not token or token_payload.get("exp") < time.time():
		doctype = frappe.get_doc(settings_doctype, username)
		token = doctype.generate_token(settings_doctype)
		frappe.db.set_value(settings_doctype, username, "token", token)
		return token, url

	return token, url


@frappe.whitelist()
def handle_employee_checkin():
	biometric_settings = frappe.get_all(
		"ZKTeco Biometric Settings", filters={"enable": 1}, fields=["username"]
	)

	for setting in biometric_settings:
		username = setting.username

		transactions = get_transactions(username)
		frappe.set_user(f"zkteco_biometric_{username}")

		for transaction in transactions:
			employee = transaction.get("emp_code")
			log_type = "IN" if transaction["punch_state_display"] == "Check-In" else "OUT"
			punch_time = transaction.get("punch_time")

			exists = frappe.db.exists(
				"Employee Checkin",
				{
					"employee": employee,
					"log_type": log_type,
					"time": punch_time,
				},
			)

			if not exists:
				frappe.get_doc(
					{
						"doctype": "Employee Checkin",
						"employee": employee,
						"log_type": log_type,
						"time": punch_time,
					}
				).insert(ignore_permissions=True)

	frappe.db.commit()
