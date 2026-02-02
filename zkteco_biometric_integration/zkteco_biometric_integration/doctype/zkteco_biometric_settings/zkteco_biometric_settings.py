# Copyright (c) 2025, Navari Limited and contributors
# For license information, please see license.txt

import time

import frappe
import jwt
import requests
from frappe.model.document import Document
from zkteco_biometric_integration.zkteco_biometric_integration.utils import (
    make_http_request,
)
from frappe.utils import get_datetime
from datetime import timedelta


class ZKTecoBiometricSettings(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        cron_expression: DF.Data | None
        enable_mandatory_checkin: DF.Check
        expiry: DF.Datetime | None
        fetch_frequency: DF.Literal[
            "All",
            "Hourly",
            "Hourly Long",
            "Hourly Maintenance",
            "Daily",
            "Daily Long",
            "Daily Maintenance",
            "Weekly",
            "Weekly Long",
            "Monthly",
            "Monthly Long",
            "Cron",
            "Yearly",
        ]
        is_fetch_enabled: DF.Check
        issued_at: DF.Datetime | None
        last_fetched_time: DF.Datetime | None
        password: DF.Data
        token: DF.Text | None
        url: DF.Data
        username: DF.Data

    def before_insert(self):
        self.last_fetched_time = get_datetime()

    def validate(self):
        self.generate_token()
        self.manage_checkin_scheduler()

    def generate_token(self) -> None:

        headers = {"Content-Type": "application/json"}

        endpoint_url = f"{self.url}/jwt-api-token-auth/"
        payload = {"username": self.username, "password": self.password}

        self.url_path = "/jwt-api-token-auth/"
        response = make_http_request(
            method="POST", url=endpoint_url, headers=headers, payload=payload
        )
        if response and response.get("token"):
            self.token = response["token"]
            self.issued_at = get_datetime()
            self.expiry = self.issued_at + timedelta(days=1)

    def manage_checkin_scheduler(self):
        method = "zkteco_biometric_integration.zkteco_biometric_integration.api.transactions_sync.handle_employee_checkin"

        job = frappe.db.exists("Scheduled Job Type", {"method": method})

        try:
            if self.is_fetch_enabled:
                if not job:
                    scheduled_job = frappe.get_doc(
                        {
                            "doctype": "Scheduled Job Type",
                            "method": method,
                            "frequency": self.fetch_frequency,
                            "stopped": 0,
                            "create_log": 1,
                            "cron_format": (
                                self.cron_expression
                                if self.fetch_frequency == "Cron"
                                else None
                            ),
                        }
                    )
                    scheduled_job.insert(ignore_permissions=True)

                frappe.db.set_value(
                    "Scheduled Job Type",
                    {"method": method},
                    {
                        "stopped": 0,
                        "frequency": self.fetch_frequency,
                        "cron_format": (
                            self.cron_expression
                            if self.fetch_frequency == "Cron"
                            else None
                        ),
                    },
                )

            else:
                if job:
                    frappe.db.set_value(
                        "Scheduled Job Type", {"method": method}, {"stopped": 1}
                    )

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), str(e))
            frappe.throw("Problem managing check-in scheduler", str(e))

    def is_token_expired(self) -> bool:
        if not self.token or not self.expiry:
            return False

        return get_datetime() >= self.expiry
