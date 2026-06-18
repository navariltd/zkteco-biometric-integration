import frappe
from frappe.model.document import Document
from frappe.utils import today

TEST_EMPLOYEE_FIRST_NAME = "_Test ZKTeco Employee"
TEST_USER_EMAIL = "_TestZKTecouser@gmail.com"
TEST_COMPANY_NAME = "_Test ZKTeco Company"


def create_settings():
	if not frappe.db.exists("ZKTeco Biometric Settings", "_Test ZKTeco Biometric Settings 1"):
		settings = frappe.get_doc(
			{
				"doctype": "ZKTeco Biometric Settings",
				"username": "_Test ZKTeco Biometric Settings 1",
				"password": "admin123",
				"url": "http://localhost:8000",
				"enable_mandatory_checkin": 1,
			}
		)
		settings.insert()
	settings = frappe.get_doc("ZKTeco Biometric Settings", "_Test ZKTeco Biometric Settings 1")
	return settings


def create_employee():
	if not frappe.db.exists("Gender", "Male"):
		frappe.get_doc({"doctype": "Gender", "gender": "Male"}).insert(ignore_permissions=True)

	company = ensure_company()

	if not frappe.db.exists(
		"Employee",
		{
			"employee_id": "EMP002",
			"first_name": TEST_EMPLOYEE_FIRST_NAME,
		},
	):
		employee = frappe.get_doc(
			{
				"doctype": "Employee",
				"employee_id": "EMP002",
				"first_name": TEST_EMPLOYEE_FIRST_NAME,
				"status": "Active",
				"gender": "Male",
				"company": company,
				"date_of_joining": today(),
				"date_of_birth": today(),
			}
		)
		employee.insert(ignore_permissions=True)

		return employee


def create_user():
	if not frappe.db.exists("User", {"email": TEST_USER_EMAIL}):
		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": TEST_USER_EMAIL,
				"first_name": "_Test ZKTeco",
				"enabled": 1,
				"roles": [{"role": "Employee"}],
			}
		)
		user.insert(ignore_permissions=True)

	user = frappe.get_doc("User", {"email": TEST_USER_EMAIL})
	return user


def cleanup_user():
	user = frappe.get_all(
		"User",
		filters={"email": TEST_USER_EMAIL},
		pluck="name",
	)

	for user_name in user:
		frappe.get_doc("User", user_name).delete(
			ignore_permissions=True,
			delete_permanently=True,
		)


def link_employee_with_user(user: Document) -> Document:
	employee = create_employee()
	employee.user_id = user.name
	employee.save(ignore_permissions=True)
	return employee


def cleanup_employee():
	employee = frappe.get_all(
		"Employee",
		filters={"first_name": TEST_EMPLOYEE_FIRST_NAME},
		pluck="name",
	)

	for emp_name in employee:
		for chk in frappe.get_all("Employee Checkin", filters={"employee": emp_name}, pluck="name"):
			frappe.get_doc("Employee Checkin", chk).delete(
				ignore_permissions=True,
				delete_permanently=True,
			)
		# Delete the employee itself
		frappe.get_doc("Employee", emp_name).delete(
			force=True,
			ignore_permissions=True,
			delete_permanently=True,
		)


def ensure_company() -> str:
	if not frappe.db.exists("Warehouse Type", "Transit"):
		frappe.get_doc({"doctype": "Warehouse Type", "name": "Transit"}).insert(ignore_permissions=True)

	if not frappe.db.exists("Company", TEST_COMPANY_NAME):
		frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": TEST_COMPANY_NAME,
				"abbr": "_TZC",
				"default_currency": "KES",
				"country": "Kenya",
			}
		).insert(ignore_permissions=True)
	return TEST_COMPANY_NAME
