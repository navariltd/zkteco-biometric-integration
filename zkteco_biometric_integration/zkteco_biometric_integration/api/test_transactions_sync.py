import frappe
import unittest
from unittest.mock import patch
from zkteco_biometric_integration.zkteco_biometric_integration.api.transactions_sync import (
    get_transactions,
    create_employee_checkin,
    manage_user,
)
from zkteco_biometric_integration.zkteco_biometric_integration.api.test_utils import (
    create_settings,
    cleanup_employee,
    create_employee,
    create_user,
    cleanup_user,
    link_employee_with_user,
)


class TestTransactionsSync(unittest.TestCase):

    @patch(
        "zkteco_biometric_integration.zkteco_biometric_integration.utils.make_http_request"
    )
    @patch(
        "zkteco_biometric_integration.zkteco_biometric_integration.doctype."
        "zkteco_biometric_settings.zkteco_biometric_settings."
        "ZKTecoBiometricSettings.generate_token"
    )
    def setUp(self, mock_generate_token, mock_make_http_request):
        frappe.set_user("Administrator")
        mock_generate_token.return_value = None

        mock_make_http_request.return_value = {"token": "test_token_123"}

        self.settings = create_settings()

    def tearDown(self):
        self.settings.delete(
            force=True,
            ignore_permissions=True,
            delete_permanently=True,
        )
        cleanup_employee()
        cleanup_user()

    @patch(
        "zkteco_biometric_integration.zkteco_biometric_integration.api.transactions_sync.make_http_request"
    )
    @patch(
        "zkteco_biometric_integration.zkteco_biometric_integration.doctype.zkteco_biometric_settings.zkteco_biometric_settings.ZKTecoBiometricSettings.is_token_expired"
    )
    def test_get_transactions(self, mock_is_token_expired, mock_make_http_request):
        mock_is_token_expired.return_value = False
        self.settings.token = "test_token_123"

        mock_make_http_request.return_value = {
            "data": [
                {"id": 1, "emp_code": "EMP001", "punch_time": "2024-01-01 09:00:00"},
                {"id": 2, "emp_code": "EMP002", "punch_time": "2024-01-01 09:15:00"},
            ],
            "next": None,
        }
        transactions = list(get_transactions(self.settings))

        self.assertEqual(len(transactions), 2)
        mock_make_http_request.assert_called_with(
            method="GET",
            url=f"{self.settings.url}/iclock/api/transactions/",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"JWT {self.settings.token}",
            },
            params=unittest.mock.ANY,
        )

    def test_create_employee_checkin_for_non_existent_employee(self):
        # Test to ensure we do not create employee checkins for non-existent employees
        transaction = {
            "id": 1,
            "emp_code": "EMP001",
            "punch_time": "2024-01-01 09:00:00",
        }

        checkin = create_employee_checkin(transaction)
        self.assertFalse(checkin)

    def test_create_employee_checkin_for_existent_employee(self):
        employee = create_employee()

        transaction = {
            "id": 1,
            "emp_code": employee.name,
            "punch_time": "2024-01-01 09:00:00",
        }

        checkin = create_employee_checkin(transaction)
        self.assertIsNotNone(checkin)
        self.assertEqual(checkin.employee, employee.name)

    def test_user_deactivation(self):
        user = create_user()
        employee = link_employee_with_user(user)
        transaction = {
            "id": 1,
            "emp_code": employee.name,
            "punch_time": "2024-01-01 09:00:00",
            "punch_state_display": "Check Out",
        }

        checkin = create_employee_checkin(transaction)
        manage_user(checkin)

        status = frappe.db.get_value("User", employee.user_id, "enabled")

        self.assertEqual(status, 0)

    def test_user_activation(self):
        user = create_user()
        employee = link_employee_with_user(user)
        transaction = {
            "id": 1,
            "emp_code": employee.name,
            "punch_time": "2024-01-01 09:00:00",
            "punch_state_display": "Check In",
        }

        checkin = create_employee_checkin(transaction)
        manage_user(checkin.as_dict())

        status = frappe.db.get_value("User", employee.user_id, "enabled")

        self.assertEqual(status, 1)
