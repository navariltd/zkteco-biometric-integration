# Copyright (c) 2026, Navari Limited and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

from zkteco_biometric_integration.zkteco_biometric_integration import (
	SCHEDULED_JOB_METHOD,
)

# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]


class IntegrationTestZKTecoGlobal(IntegrationTestCase):
	"""
	Integration tests for ZKTecoGlobal.
	Use this class for testing interactions between multiple components.
	"""

	def test_save_with_non_cron_frequency(self):
		doc = frappe.get_doc("ZKTeco Global")
		doc.fetch_frequency = "All"
		doc.cron_expression = None
		doc.save()

		job = frappe.get_doc("Scheduled Job Type", {"method": SCHEDULED_JOB_METHOD})
		self.assertEqual(job.frequency, "All")
		self.assertEqual(job.cron_format or "", "")

	def test_save_cron_frequency(self):
		doc = frappe.get_doc("ZKTeco Global")
		doc.fetch_frequency = "Cron"
		doc.cron_expression = "*/15 * * * *"
		doc.save()

		job = frappe.get_doc("Scheduled Job Type", {"method": SCHEDULED_JOB_METHOD})
		self.assertEqual(job.frequency, "Cron")
		self.assertEqual(job.cron_format, "*/15 * * * *")

	def test_cron_without_expression_throws(self):
		doc = frappe.get_doc("ZKTeco Global")
		doc.fetch_frequency = "Cron"
		doc.cron_expression = None
		self.assertRaises(frappe.ValidationError, doc.save)
