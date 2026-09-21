"""Tests for the sweep report: `make test-sweep`.

A report is read long after it was produced, so what it prints has to follow
from what it recorded and nothing else: the columns a sweep asked for, and the
same tables every time it is rendered.
"""

import csv
import glob
import json
import os
import shutil
import sys
import tempfile
import unittest

# No __pycache__ beside sweep.py: nothing in this repository ignores it.
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sweep  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def recorded(directory, definition):
    """A report directory as a sweep leaves it, with made-up numbers."""
    with open(os.path.join(directory, "sweep.json"), "w") as f:
        json.dump(definition, f)
    rows = []
    for labels, _ in sweep.combinations(definition):
        for seed in definition["seeds"]:
            row = {field: 10 * seed for field in sweep.METRICS}
            rows.append({**row, **labels, "seed": seed})
    fields = [a["name"] for a in definition["axes"]] + ["seed"] + sweep.METRICS
    with open(os.path.join(directory, "runs.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    build = {"version": "1.0.0", "commit": "0" * 40, "modified": False}
    with open(os.path.join(directory, "provenance.json"), "w") as f:
        json.dump({"recorded_at": "2026-09-21T00:00:00+00:00", "command": "make sweep S=t",
                   "simlab_api": build, "autoscaler": build, "runs": len(rows),
                   "runs_csv_sha256": "0" * 64}, f)


def definition(**extra):
    return {
        "name": "t", "title": "T", "question": "Q?", "seeds": [1, 2],
        "axes": [{"name": "day", "values": [{"label": "workday"}, {"label": "rock burst"}]},
                 {"name": "setting", "values": [{"label": "calibrated"}, {"label": "more cloud"}]}],
        "baseline": {"setting": "calibrated"},
        **extra,
    }


def header_after(report_md, heading_prefix):
    lines = report_md.splitlines()
    start = next(i for i, line in enumerate(lines) if line.lstrip("# ").startswith(heading_prefix))
    return next(line for line in lines[start:] if line.startswith("| Arm"))


class TestColumns(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)

    def render(self, sweep_definition):
        recorded(self.dir, sweep_definition)
        sweep.write_report(self.dir, notes_path=os.path.join(self.dir, "no-notes.md"))
        with open(os.path.join(self.dir, "report.md")) as f:
            return f.read()

    def test_a_sweep_that_names_no_columns_reports_what_intent_changes(self):
        report = self.render(definition())
        self.assertEqual(header_after(report, "Results"),
                         "| Arm | Breaches | As submitted | Cloud h | Drained h | Overloads | Exposing events "
                         "| Locate exposing, mean s | p95 s | Process exposing, mean s | Locate all, mean s "
                         "| Exposing decayed | Events decayed |")
        self.assertEqual(header_after(report, "Against"),
                         "| Arm | Breaches | As submitted | Cloud h | Locate exposing, mean | Process exposing, mean |")

    def test_a_sweep_that_names_its_columns_reports_and_compares_only_those(self):
        report = self.render(definition(columns=["sla_breaches", "cloud_hours", "p95_wait_s"],
                                        compare=["sla_breaches", "p95_wait_s"]))
        self.assertEqual(header_after(report, "Results"), "| Arm | Breaches | Cloud h | Wait p95 s |")
        self.assertEqual(header_after(report, "Against"), "| Arm | Breaches | Wait p95 |")

    def test_a_named_column_is_defined_and_one_not_shown_is_not(self):
        report = self.render(definition(columns=["sla_breaches", "local_hours"]))
        meaning = report.split("## What the columns mean", 1)[1].split("## Setup", 1)[0]
        self.assertIn("**Local h**", meaning)
        self.assertNotIn("Exposing decayed", meaning)

    def test_a_column_a_report_cannot_show_is_refused_naming_the_ones_it_can(self):
        with self.assertRaisesRegex(ValueError, r"columns names peak_cloud, .*it can show sla_breaches, "):
            sweep.headline(definition(columns=["peak_cloud", "sla_breaches"]))

    def test_every_column_a_report_can_show_is_measured_and_defined(self):
        for field in sweep.COLUMNS:
            self.assertIn(field, sweep.METRICS)
            self.assertIn(field, sweep.DEFINED)


class TestBuilds(unittest.TestCase):
    def test_a_service_a_sweep_does_not_pin_is_built_from_head(self):
        self.assertEqual(sweep.build_ref(definition(build={"simlab-api": "v3.0.0"}), "autoscaler"), "HEAD")

    def test_a_pinned_service_is_built_from_its_pin(self):
        self.assertEqual(sweep.build_ref(definition(build={"simlab-api": "v3.0.0"}), "simlab-api"), "v3.0.0")

    def test_a_pin_for_something_a_sweep_does_not_build_is_refused_naming_what_it_does(self):
        with self.assertRaisesRegex(ValueError, r"build names simlab-web; a sweep builds autoscaler, simlab-api"):
            sweep.build_ref(definition(build={"simlab-web": "v1.0.0"}), "autoscaler")


class TestRecordedReports(unittest.TestCase):
    def test_every_recorded_report_renders_again_as_it_was_printed(self):
        checked = 0
        for original in sorted(glob.glob(os.path.join(ROOT, "reports", "*", "sweep.json"))):
            directory = os.path.dirname(original)
            name = os.path.basename(directory)
            with tempfile.TemporaryDirectory() as copy:
                for part in ("sweep.json", "provenance.json", "runs.csv"):
                    shutil.copy(os.path.join(directory, part), copy)
                sweep.write_report(copy, notes_path=os.path.join(ROOT, "sweeps", name + ".md"))
                with open(os.path.join(copy, "report.md")) as again, open(os.path.join(directory, "report.md")) as was:
                    # The last line names the commit that rendered the tables.
                    self.assertEqual(again.read().splitlines()[:-2], was.read().splitlines()[:-2], name)
            checked += 1
        self.assertGreater(checked, 0, "no recorded reports were found, so nothing was checked")


if __name__ == "__main__":
    unittest.main()
