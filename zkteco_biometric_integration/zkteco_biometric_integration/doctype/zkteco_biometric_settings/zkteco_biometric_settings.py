# Copyright (c) 2025, Navari Limited and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe.model.document import Document


class ZKTecoBiometricSettings(Document):
	def before_save(self):
		self.token = self.generate_token()
		frappe.msgprint("Token generated succeesfully")

	def generate_token(self):
		headers = {"Content-Type": "application/json"}

		payload = {"username": self.username, "password": self.password}
		self.url_path = "/jwt-api-token-auth/"

		endpoint_url = f"{self.url}{self.url_path}"

		try:
			response = requests.post(endpoint_url, payload, headers)

			if response.status_code == 200:
				print("jwt token successful", response.text)
				return response.json().get("token")
			else:
				frappe.throw(f"Problem generating Token: {response.json().get("detail")}")

		except Exception as e:
			frappe.throw("Problem generating Token", str(e))
