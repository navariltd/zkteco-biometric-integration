# Copyright (c) 2025, Navari Limited and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import get_datetime
from unittest.mock import patch
from datetime import timedelta

SCHEDULED_JOB_METHOD = "zkteco_biometric_integration.zkteco_biometric_integration.api.transactions_sync.handle_employee_checkin"


def create_settings():
    if not frappe.db.exists(
        "ZKTeco Biometric Settings", "__Test ZKTeco Biometric Settings 1"
    ):
        settings = frappe.get_doc(
            {
                "doctype": "ZKTeco Biometric Settings",
                "username": "__Test ZKTeco Biometric Settings 1",
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
        "ZKTecoBiometricSettings.manage_checkin_scheduler"
    )
    @patch(
        "zkteco_biometric_integration.zkteco_biometric_integration.doctype."
        "zkteco_biometric_settings.zkteco_biometric_settings."
        "ZKTecoBiometricSettings.generate_token"
    )
    def setUp(self, mock_generate_token, mock_manage_checkin_scheduler):
        mock_generate_token.return_value = None
        mock_manage_checkin_scheduler.return_value = None
        self.settings = create_settings()

    def tearDown(self):
        self.settings.delete()

    def test_create_last_fetched_time(self):
        self.assertIsNotNone(self.settings.last_fetched_time)
        self.assertAlmostEqual(
            self.settings.last_fetched_time, get_datetime(), delta=timedelta(seconds=1)
        )

    def test_create_manage_checkin_scheduler(self):
        self.settings.is_fetch_enabled = 1
        self.settings.fetch_frequency = "All"
        self.assertTrue(
            frappe.db.exists("Scheduled Job Type", {"method": SCHEDULED_JOB_METHOD})
        )
