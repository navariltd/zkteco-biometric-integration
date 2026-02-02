import requests
import frappe
from typing import Literal
from frappe.model.document import Document
from datetime import datetime, date, time
from typing import Callable

methodMap: dict[str, Callable[..., requests.Response]] = {
    "GET": requests.get,
    "POST": requests.post,
}


def http_type_method(method: str) -> Callable[..., requests.Response]:

    if method not in methodMap:
        frappe.throw(f"HTTP Method {method} not supported")

    return methodMap[method]


def make_http_request(
    method: str,
    url: str,
    headers: dict[str, str],
    payload: dict | None = None,
    params: dict | None = None,
) -> dict | None:

    http_method = http_type_method(method)

    try:
        response = http_method(url, headers=headers, json=payload, params=params)

        response.raise_for_status()
        return response.json()

    except Exception as e:
        frappe.log_error(
            message=frappe.get_traceback(), title="ZKTeco Biometric Integration"
        )
        frappe.throw(f"HTTP Request failed: {e}")


def update_integration_request_log(
    integration_request_log: Document,
    status: Literal["Completed", "Failed"],
    response: dict | None = None,
    error: str | None = None,
) -> None:

    if not integration_request_log:
        return

    integration_request_log.status = str(status)
    integration_request_log.output = str(response)
    integration_request_log.error = str(error)

    integration_request_log.save(ignore_permissions=True)


def map_checkin(punch_state: str) -> str:
    punch_state_map = {
        "Check In": "IN",
        "Check Out": "OUT",
    }

    checkin_state = punch_state_map.get(punch_state)
    if not checkin_state:
        frappe.log_error(f"Unknown punch state: {punch_state}")
        return
    return checkin_state


def get_employees() -> list[dict]:
    return frappe.get_all(
        "Employee",
        filters={"status": "Active"},
    )


def get_day_time_range() -> list[datetime]:

    today = date.today()
    start_of_day = datetime.combine(today, time())
    end_of_day = datetime.combine(today, time(23, 59, 59))
    return [start_of_day, end_of_day]


def does_checkin_exist(employee: str):
    return frappe.db.exists(
        "Employee Checkin",
        {
            "employee": employee,
            "log_type": "IN",
            "time": ["between", get_day_time_range()],
        },
    )


def does_checkin_exist(transaction: dict) -> bool:
    return frappe.db.exists(
        "Employee Checkin",
        {
            "employee": transaction.get("emp_code"),
            "time": transaction.get("punch_time"),
            "log_type": map_checkin(transaction.get("punch_state_display")),
        },
    )


def does_employee_exist(emp_code: str) -> bool:
    return frappe.db.exists(
        "Employee",
        {
            "name": emp_code,
            "status": "Active",
        },
    )
