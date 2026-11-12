"""Manage interactions with the report.json file."""

import json

from buildscripts.resmokelib import config
from buildscripts.resmokelib.testing import report as _report


def _suite_name(suite):
    """Return the suite name to record, using the original suite for generated sub-suites."""
    return config.ORIGIN_SUITE or suite.get_name()


def write(suites):
    """Write the combined report of all executions if --reportFile was specified."""

    if config.REPORT_FILE is None:
        return

    combined_report_dict = {"results": [], "failures": 0}

    for suite in suites:
        suite_report_dict = _report.TestReport.combine(*suite.get_reports()).as_dict()
        suite_name = _suite_name(suite)
        for result in suite_report_dict["results"]:
            result["suite"] = suite_name
        combined_report_dict["results"].extend(suite_report_dict["results"])
        combined_report_dict["failures"] += suite_report_dict["failures"]

    for suite in suites:
        for test_name in getattr(suite, "_tss_skipped_tests", []):
            combined_report_dict["results"].append(
                {
                    "test_file": test_name,
                    "suite": _suite_name(suite),
                    "status": "skip",
                    "exit_code": 0,
                    "start": 0,
                    "end": 0,
                    "elapsed": 0,
                    "log_info": {},
                }
            )

    with open(config.REPORT_FILE, "w") as fp:
        json.dump(combined_report_dict, fp)
