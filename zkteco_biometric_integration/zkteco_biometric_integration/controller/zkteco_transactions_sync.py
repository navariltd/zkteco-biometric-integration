import frappe
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
		frappe.throw("Problem generating transactions", str(e))


@frappe.whitelist(allow_guest=True)
def get_configs(username):
	settings_doctype = "ZKTeco Biometric Settings"
	token, url = frappe.db.get_value(settings_doctype, username, ["token", "url"])

	if not token:
		token = ZKTecoBiometricSettings.generate_token()
		frappe.db.set_value(settings_doctype, username, "token", token)
		return token

	return token, url
