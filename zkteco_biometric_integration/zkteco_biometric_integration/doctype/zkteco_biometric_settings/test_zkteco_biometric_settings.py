# Copyright (c) 2025, Navari Limited and Contributors
# See license.txt

from datetime import timedelta
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import get_datetime

from zkteco_biometric_integration.zkteco_biometric_integration import (
	SCHEDULED_JOB_METHOD,
)

SETTINGS_NAME = "__Test ZKTeco Biometric Settings 1"


def create_settings():
	if frappe.db.exists("ZKTeco Biometric Settings", SETTINGS_NAME):
		frappe.delete_doc(
			"ZKTeco Biometric Settings",
			SETTINGS_NAME,
			force=True,
			ignore_permissions=True,
			delete_permanently=True,
		)

	settings = frappe.get_doc(
		{
			"doctype": "ZKTeco Biometric Settings",
			"username": SETTINGS_NAME,
			"password": "admin123",
			"url": "http://localhost:8000",
		}
	)
	settings.insert()
	return settings


class TestZKTecoBiometricSettings(FrappeTestCase):
	@patch(
		"zkteco_biometric_integration.zkteco_biometric_integration.doctype."
		"zkteco_biometric_settings.zkteco_biometric_settings."
		"ZKTecoBiometricSettings.generate_token"
	)
	def setUp(self, mock_generate_token):
		mock_generate_token.return_value = None
		self.settings = create_settings()

	def tearDown(self):
		self.settings.delete(
			force=True,
			ignore_permissions=True,
			delete_permanently=True,
		)

	def test_create_last_fetched_time(self):
		self.assertIsNotNone(self.settings.last_fetched_time)
		self.assertAlmostEqual(
			self.settings.last_fetched_time,
			get_datetime(),
			delta=timedelta(seconds=1),
		)

	def test_scheduled_job_type_exists(self):
		self.assertTrue(frappe.db.exists("Scheduled Job Type", {"method": SCHEDULED_JOB_METHOD}))
