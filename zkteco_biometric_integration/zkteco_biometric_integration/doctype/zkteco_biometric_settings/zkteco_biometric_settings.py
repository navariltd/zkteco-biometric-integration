# Copyright (c) 2025, Navari Limited and contributors
# For license information, please see license.txt

import time
from datetime import timedelta

import frappe
import jwt
import requests
from frappe.model.document import Document
from frappe.utils import get_datetime

from zkteco_biometric_integration.zkteco_biometric_integration.utils import (
	make_http_request,
)


class ZKTecoBiometricSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		enable_mandatory_checkin: DF.Check
		expiry: DF.Datetime | None
		is_fetch_enabled: DF.Check
		issued_at: DF.Datetime | None
		last_fetched_time: DF.Datetime | None
		password: DF.Data
		token: DF.Text | None
		url: DF.Data
		username: DF.Data
	# end: auto-generated types

	def after_insert(self):
		self.db_set("last_fetched_time", get_datetime())

	def validate(self):
		self.generate_token()

	def generate_token(self) -> None:
		headers = {"Content-Type": "application/json"}

		endpoint_url = f"{self.url}/jwt-api-token-auth/"
		payload = {"username": self.username, "password": self.password}

		response = make_http_request(method="POST", url=endpoint_url, headers=headers, payload=payload)
		if response and response.get("token"):
			self.token = response["token"]
			self.issued_at = get_datetime()
			self.expiry = self.issued_at + timedelta(days=1)

	def is_token_expired(self) -> bool:
		if not self.token or not self.expiry:
			return False

		return get_datetime() >= self.expiry
