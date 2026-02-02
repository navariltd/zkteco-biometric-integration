import frappe
from frappe.model.document import Document
from zkteco_biometric_integration.zkteco_biometric_integration.utils import (
    make_http_request,
    update_integration_request_log,
    map_checkin,
    does_checkin_exist,
    does_employee_exist,
)
from frappe.utils import get_datetime
from frappe.integrations.utils import create_request_log


@frappe.whitelist()
def handle_employee_checkin():

    biometric_settings = frappe.get_all(
        "ZKTeco Biometric Settings", filters={"is_fetch_enabled": 1}
    )

    for setting in biometric_settings:
        setting_doc = frappe.get_doc("ZKTeco Biometric Settings", setting.name)

        transactions = get_transactions(setting_doc)
        if not transactions:
            return

        for txn in transactions:
            if emp_checkin := create_employee_checkin(txn):
                (
                    manage_user(emp_checkin)
                    if setting_doc.enable_mandatory_checkin
                    else None
                )


@frappe.whitelist(allow_guest=True)
def get_transactions(setting_doc: Document) -> list[dict]:

    if setting_doc.is_token_expired():
        setting_doc.save()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"JWT {setting_doc.token}",
    }

    url = f"{setting_doc.url}/iclock/api/transactions/"

    start_time = (
        setting_doc.last_fetched_time
        if setting_doc.last_fetched_time
        else get_datetime()
    )
    end_time = get_datetime()

    params = {
        "start_time": (start_time.strftime("%Y-%m-%d %H:%M:%S")),
        "end_time": (end_time.strftime("%Y-%m-%d %H:%M:%S")),
    }

    integration_request_log = create_request_log(
        data=params,
        integration_type="Remote",
        service_name="ZKTeco Biometric Integration",
        request_headers=headers,
        request_url=url,
        reference_doctype="ZKTeco Biometric Settings",
        reference_docname=setting_doc.name,
    )
    all_transactions = []

    try:
        while url:
            response = make_http_request(
                method="GET", url=url, headers=headers, params=params
            )

            if response and response.get("data"):
                all_transactions.extend(response["data"])

                url = response.get("next")
                params = None
            else:
                break

        if all_transactions:

            frappe.db.set_value(
                "ZKTeco Biometric Settings",
                setting_doc.name,
                "last_fetched_time",
                end_time,
            )

            update_integration_request_log(
                integration_request_log, status="Completed", response=response
            )

        return all_transactions
    except Exception as e:
        update_integration_request_log(
            integration_request_log, status="Failed", error=str(e)
        )
        frappe.log_error(frappe.get_traceback(), str(e))


def create_employee_checkin(transaction: dict) -> None:

    validation_rules = [
        lambda: does_checkin_exist(transaction),
        lambda: not does_employee_exist(transaction.get("emp_code")),
    ]

    if any(rule() for rule in validation_rules):
        return

    try:
        frappe.set_user("ZKTeco Biometric")
        employee_checkin = frappe.get_doc(
            {
                "doctype": "Employee Checkin",
                "employee": transaction.get("emp_code"),
                "time": transaction.get("punch_time"),
                "log_type": map_checkin(transaction.get("punch_state_display")),
            }
        )
        employee_checkin.insert(ignore_permissions=True)
        return employee_checkin

    except Exception as e:
        frappe.log_error(
            title="Employee Checkin Creation Error", message=frappe.get_traceback()
        )
    finally:
        frappe.set_user("Guest")


def activate_user(user_id: str, log_type: str) -> None:
    try:
        if "System Manager" in frappe.get_roles(user_id):
            return

        should_enable = log_type == "IN"

        frappe.db.set_value(
            "User", user_id, "enabled", int(should_enable), update_modified=False
        )

    except Exception:
        frappe.log_error(message=frappe.get_traceback(), title="User Activation Error")


def manage_user(employee_checkin: Document):
    if frappe.db.exists("Employee", employee_checkin.employee):
        employee = frappe.get_doc("Employee", employee_checkin.employee)

        if employee.user_id:
            activate_user(employee.user_id, employee_checkin.log_type)
