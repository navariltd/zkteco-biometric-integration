import frappe

__version__ = "0.0.1"


def is_website_user(username: str | None = None) -> str | None:
	return frappe.db.get_value("User", username or frappe.session.user, "user_type") == "Website User"


def check_app_permission():
	if frappe.session.user == "Administrator":
		return True

	if is_website_user():
		return False

	return True
