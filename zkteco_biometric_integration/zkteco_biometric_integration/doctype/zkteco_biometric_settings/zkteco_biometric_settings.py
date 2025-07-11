# Copyright (c) 2025, Navari Limited and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe.model.document import Document


class ZKTecoBiometricSettings(Document):
	def before_save(self):
		self.token = self.generate_token()
		frappe.msgprint("Token generated succesfully")

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
