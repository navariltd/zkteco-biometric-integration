import unittest
from unittest.mock import patch

import frappe

from zkteco_biometric_integration.zkteco_biometric_integration.api.test_utils import (
	cleanup_employee,
	cleanup_user,
	create_employee,
	create_settings,
	create_user,
	link_employee_with_user,
)
from zkteco_biometric_integration.zkteco_biometric_integration.api.transactions_sync import (
	create_employee_checkin,
	get_transactions,
	manage_user,
)


class TestTransactionsSync(unittest.TestCase):
	@patch("zkteco_biometric_integration.zkteco_biometric_integration.utils.make_http_request")
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
			"punch_state_display": "Check In",
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

	@patch(
		"zkteco_biometric_integration.zkteco_biometric_integration.api.transactions_sync.make_http_request"
	)
	@patch(
		"zkteco_biometric_integration.zkteco_biometric_integration.doctype.zkteco_biometric_settings.zkteco_biometric_settings.ZKTecoBiometricSettings.is_token_expired"
	)
	def test_sync_creates_checkins_from_zkteco_payload(self, mock_is_token_expired, mock_make_http_request):
		"""End-to-end: a realistic paginated ZKTeco /iclock/api/transactions/
		payload results in Employee Checkin documents."""
		mock_is_token_expired.return_value = False
		self.settings.token = "test_token_123"

		employee = create_employee()

		# Mirrors the real BioTime transaction interface, across two pages
		# to exercise the pagination loop.
		page_2_url = f"{self.settings.url}/iclock/api/transactions/?page=2"
		mock_make_http_request.side_effect = [
			{
				"count": 2,
				"next": page_2_url,
				"previous": None,
				"data": [
					{
						"id": 101,
						"emp_code": employee.name,
						"punch_time": "2024-01-02 08:30:00",
						"punch_state": "0",
						"punch_state_display": "Check In",
						"verify_type": 1,
						"verify_type_display": "Fingerprint",
						"terminal_sn": "CJDE193560303",
						"terminal_alias": "Main Gate",
						"area_alias": "HQ",
						"upload_time": "2024-01-02 08:30:05",
					},
				],
			},
			{
				"count": 2,
				"next": None,
				"previous": None,
				"data": [
					{
						"id": 102,
						"emp_code": employee.name,
						"punch_time": "2024-01-02 17:45:00",
						"punch_state": "1",
						"punch_state_display": "Check Out",
						"verify_type": 1,
						"verify_type_display": "Fingerprint",
						"terminal_sn": "CJDE193560303",
						"terminal_alias": "Main Gate",
						"area_alias": "HQ",
						"upload_time": "2024-01-02 17:45:04",
					},
				],
			},
		]

		transactions = list(get_transactions(self.settings))
		self.assertEqual(len(transactions), 2)

		checkins = [create_employee_checkin(txn) for txn in transactions]
		self.assertTrue(all(checkins))

		# Verify against the DB, not just returned objects
		in_punch = frappe.db.get_value(
			"Employee Checkin",
			{"employee": employee.name, "time": "2024-01-02 08:30:00"},
			"log_type",
		)
		out_punch = frappe.db.get_value(
			"Employee Checkin",
			{"employee": employee.name, "time": "2024-01-02 17:45:00"},
			"log_type",
		)
		self.assertEqual(in_punch, "IN")
		self.assertEqual(out_punch, "OUT")

		# Pagination was followed: first call with params, second to the next URL
		self.assertEqual(mock_make_http_request.call_count, 2)
		second_call_kwargs = mock_make_http_request.call_args_list[1].kwargs
		self.assertEqual(second_call_kwargs["url"], page_2_url)
		self.assertIsNone(second_call_kwargs["params"])

		# Idempotency: re-running the same payload creates no duplicates
		duplicate = create_employee_checkin(transactions[0])
		self.assertIsNone(duplicate)
		total = frappe.db.count("Employee Checkin", {"employee": employee.name})
		self.assertEqual(total, 2)
