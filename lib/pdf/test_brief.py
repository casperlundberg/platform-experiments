"""Tests for the brief renderer: `make test-pdf`.

The property that matters most is the first one: a brief quotes the reports,
so every number a chart can draw must be the number its report printed.
"""

import glob
import os
import shutil
import sys
import tempfile
import unittest

# No __pycache__ beside lib/sweep.py and this package: nothing in this repository
# ignores it, and it is not source.
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from render import render  # noqa: E402
from sources import ROOT, BriefError, Report, Reports, load_yaml, stamp  # noqa: E402

import sweep  # noqa: E402,I100  (after sources, which puts lib/ on the path)

REPORTS = sorted(os.path.dirname(p) for p in glob.glob(os.path.join(ROOT, "reports", "*", "sweep.json")))
CHANGED = ("sla_breaches", "sla_breaches_as_submitted", "cloud_hours", "ttl_exposing_mean_s", "ttp_exposing_mean_s")


def printed_table(report_md, heading_prefix):
    """The rows of the first table under a heading, keyed by their first cell."""
    rows, inside = {}, False
    for line in report_md.splitlines():
        if line.startswith("#"):
            inside = line.lstrip("# ").startswith(heading_prefix)
            continue
        if inside and line.startswith("| ") and not line.startswith("|---"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows[cells[0]] = cells[1:]
    return rows


def brief(directory, body, header="title: A brief\n"):
    path = os.path.join(directory, "brief.md")
    with open(path, "w") as f:
        f.write(f"---\n{header}---\n\n{body}\n")
    return path


class TestChartsQuoteTheirReports(unittest.TestCase):
    def test_every_change_a_chart_can_show_is_the_one_its_report_printed(self):
        compared = 0
        for directory in REPORTS:
            report = Report(directory)
            if not report.baseline:
                continue
            printed = printed_table(report.text(), "Against")
            for labels, _ in sweep.combinations(report.sweep):
                if {**labels, **report.baseline} == labels:
                    continue
                row = printed[sweep.arm_name(labels)]
                for field, cell in zip(CHANGED, row):
                    value = report.change(labels, field)
                    self.assertEqual(f"{value * 100:+.0f} %" if value is not None else "–", cell,
                                     f"{report.path}, {sweep.arm_name(labels)}, {field}")
                    compared += 1
        self.assertGreater(compared, 300, "the comparison tables were not found, so nothing was checked")

    def test_every_mean_a_chart_can_show_is_the_one_its_report_printed(self):
        compared = 0
        for directory in REPORTS:
            report = Report(directory)
            printed = printed_table(report.text(), "Results")
            for labels, _ in sweep.combinations(report.sweep):
                row = printed[sweep.arm_name(labels)]
                for (field, _, places), cell in zip(sweep.HEADLINE, row):
                    self.assertEqual(sweep.cell(report.mean(labels, field), places), cell,
                                     f"{report.path}, {sweep.arm_name(labels)}, {field}")
                    compared += 1
        self.assertGreater(compared, 1000, "the results tables were not found, so nothing was checked")


class TestRefusals(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)

    def test_runs_that_no_longer_match_their_recorded_digest_are_refused(self):
        copy = os.path.join(self.dir, "pick-jitter")
        shutil.copytree(os.path.join(ROOT, "reports", "pick-jitter"), copy)
        with open(os.path.join(copy, "runs.csv"), "a") as f:
            f.write("\n")
        with self.assertRaisesRegex(BriefError, r"runs\.csv has SHA-256 .* but its provenance recorded"):
            Report(copy)

    def test_a_chart_that_would_average_several_arms_together_is_refused_naming_the_open_axis(self):
        with self.assertRaisesRegex(BriefError, r"nothing fixes axis 'knowledge'"):
            Reports().get("reports/intent-modes").mean({"intent": "off"}, "sla_breaches")

    def test_a_character_no_font_carries_is_refused_and_named(self):
        path = brief(self.dir, "A word no font here has: 漢.")
        with self.assertRaisesRegex(BriefError, r"U\+6F22 .* is not in Serif; first at .*brief\.md:5"):
            render(path, os.path.join(self.dir, "out.pdf"))

    def test_a_table_row_the_report_does_not_have_is_refused_with_the_rows_it_does(self):
        path = brief(self.dir, "```table\nfrom: reports/workforce\nsection: Against off, at the same workforce\n"
                               "rows: [nobody]\n```")
        with self.assertRaisesRegex(BriefError, r"no row 'nobody' \(rows: small crew"):
            render(path, os.path.join(self.dir, "out.pdf"))

    def test_bars_on_a_log_scale_are_refused(self):
        path = brief(self.dir, "```chart\nsource: reports/workforce\nx: workforce\nwhere: {intent: off}\n"
                               "y: [{measure: sla_breaches, log: true}]\n```")
        with self.assertRaisesRegex(BriefError, r"bars need a zero baseline"):
            render(path, os.path.join(self.dir, "out.pdf"))


class TestRendering(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)

    def test_the_same_brief_renders_to_the_same_bytes(self):
        path = brief(self.dir, EVERYTHING, header="title: Twice\ndate: 2026-09-21\ntoc: true\n")
        first, second = os.path.join(self.dir, "a.pdf"), os.path.join(self.dir, "b.pdf")
        pages = render(path, first)
        render(path, second)
        with open(first, "rb") as a, open(second, "rb") as b:
            self.assertEqual(a.read(), b.read())
        self.assertGreaterEqual(pages, 2)

    def test_off_is_an_arm_not_a_boolean(self):
        self.assertEqual(load_yaml("where: {intent: off}\nrange: false"), {"where": {"intent": "off"}, "range": False})

    def test_an_input_outside_the_repository_always_counts_as_uncommitted(self):
        outside = brief(self.dir, "text")
        self.assertIn(outside, stamp([outside])["modified"])


EVERYTHING = """# Summary {-}

Plain, **bold**, *italic*, `code`, a [link](https://example.org) and − × ± → ≈.

- a list
  - nested

> **A callout.** Inside a box.

| Arm | Value |
|---|---:|
| a | 1,687<br><sub>950–2,119</sub> |

Table: A caption.

# Figures

```chart
source: reports/scenario-shapes
kind: dots
x: shape
series: intent
where: {intent: [off, "decay to its own level"]}
y: [{measure: sla_breaches, label: Breaches, log: true}]
caption: Dots.
```

```chart
source: reports/lookahead-uncertainty
kind: lines
x: uncertainty
series: lookahead
ramp: true
where: {intent: "decay, restored exempt"}
y: [{measure: sla_breaches, label: Breaches vs no intent, change: true}]
caption: Lines.
```

```table
from: reports/intent-modes
section: Against off · estimate
rows: ["decay, restored exempt · estimate"]
caption: Lifted.
```

<!-- pagebreak -->

```provenance
```
"""


if __name__ == "__main__":
    unittest.main()
