import time

import frappe
import jwt
import requests


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
			frappe.throw(f"Error generating transactions: {response.json().get("detail")}")

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), str(e))
		frappe.throw("Problem generating transactions", str(e))


def get_configs(username):
	settings = frappe.get_doc("NL ZKTeco Biometric Settings", username)
	if not settings:
		frappe.throw(f"Biometric Settings with {username} not found")
		frappe.log_error(
			f"Biometric Settings with {username} not found",
			"ZKTeco Biometric Integration",
		)
	token, url = settings.get_settings()

	return token, url


@frappe.whitelist()
def handle_employee_checkin():
	biometric_settings = frappe.get_all(
		"NL ZKTeco Biometric Settings", filters={"enable": 1}, fields=["username"]
	)
	if not biometric_settings:
		frappe.throw("No Biometric Settings found")
		frappe.log_error("No Biometric Settings found", "ZKTeco Biometric Integration")

	for setting in biometric_settings:
		username = setting.username

		transactions = get_transactions(username)

		try:
			frappe.set_user(f"zkteco_biometric_{username}")

			for transaction in transactions:
				employee = transaction.get("emp_code")
				if not frappe.db.exists("Employee", employee):
					return
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
		except Exception as e:
			frappe.db.rollback()
			frappe.log_error(frappe.get_traceback(), str(e))
			frappe.throw("Problem handling employee check-in", str(e))
		finally:
			frappe.set_user("Guest")
