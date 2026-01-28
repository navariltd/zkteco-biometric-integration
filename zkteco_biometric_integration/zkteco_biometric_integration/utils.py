import requests
import frappe
from typing import Literal
from frappe.model.document import Document

methodMap: dict[str, callable] = {
    "GET": requests.get,
    "POST": requests.post,
}


def http_type_method(method: str) -> callable:

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
