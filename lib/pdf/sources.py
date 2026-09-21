"""What a brief reads: sweep reports, the runs behind them, and git.

Every number a brief shows comes from a report directory as a sweep wrote it,
never retyped, and through the same helpers the report writer uses — so a
figure cannot drift from the table it summarises.
"""

import hashlib
import json
import os
import re
import subprocess
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "lib"))

import sweep  # noqa: E402  (the report writer's own aggregation, deliberately shared)


class BriefError(Exception):
    """A brief that cannot be rendered truthfully, and why."""


class _Loader(yaml.SafeLoader):
    pass


# YAML 1.1 reads off, on, yes and no as booleans, and "off" is the label of the
# arm most charts compare against: `where: {intent: off}` would silently ask for
# an arm called False. Only true and false are booleans here, as in YAML 1.2.
_Loader.yaml_implicit_resolvers = {
    first: [(tag, pattern) for tag, pattern in resolvers if tag != "tag:yaml.org,2002:bool"]
    for first, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()}
_Loader.add_implicit_resolver("tag:yaml.org,2002:bool", re.compile(r"^(?:true|True|TRUE|false|False|FALSE)$"),
                              list("tTfF"))


def load_yaml(text):
    return yaml.load(text, Loader=_Loader)


def resolve(path):
    return path if os.path.isabs(path) else os.path.join(ROOT, path)


def relative(path):
    path = os.path.abspath(path)
    return os.path.relpath(path, ROOT) if path.startswith(ROOT + os.sep) else path


class Report:
    """One sweep's report directory: its definition, provenance and runs."""

    def __init__(self, path):
        self.path = relative(resolve(path))
        self.dir = resolve(path)
        if not os.path.isdir(self.dir):
            raise BriefError(f"{self.path}: no such report directory (expected reports/NAME, as `make sweep` writes)")
        for name in ("sweep.json", "provenance.json", "runs.csv", "report.md"):
            if not os.path.exists(os.path.join(self.dir, name)):
                raise BriefError(f"{self.path}: has no {name}; is it a sweep's report directory?")
        with open(os.path.join(self.dir, "sweep.json")) as f:
            self.sweep = json.load(f)
        with open(os.path.join(self.dir, "provenance.json")) as f:
            self.provenance = json.load(f)

        # A report's numbers are evidence because runs.csv is what the recorded
        # builds produced. If it has changed since, a figure drawn from it would
        # quote numbers no build is on record as producing.
        with open(os.path.join(self.dir, "runs.csv"), "rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()
        recorded = self.provenance.get("runs_csv_sha256")
        if digest != recorded:
            raise BriefError(
                f"{self.path}/runs.csv has SHA-256 {digest[:16]}…, but its provenance recorded "
                f"{(recorded or 'none')[:16]}…: the runs are not the ones the recorded builds produced. "
                f"Rerun the sweep rather than editing its results.")

        self.rows = sweep.read_rows(self.dir)
        self.axes = [axis["name"] for axis in self.sweep["axes"]]
        self.baseline = self.sweep.get("baseline") or {}

    @property
    def name(self):
        return os.path.basename(self.dir.rstrip(os.sep))

    def labels(self, axis):
        """An axis's labels in the order the sweep defines them."""
        self.require_axis(axis)
        definition = next(a for a in self.sweep["axes"] if a["name"] == axis)
        return [value["label"] for value in definition["values"]]

    def require_axis(self, axis):
        if axis not in self.axes:
            raise BriefError(f"{self.path} has no axis '{axis}' (its axes: {', '.join(self.axes)})")

    def require_measure(self, field):
        if not self.rows or field not in self.rows[0]:
            columns = [c for c in (self.rows[0] if self.rows else {}) if c not in self.axes and c != "seed"]
            raise BriefError(f"{self.path}/runs.csv has no column '{field}' (measures: {', '.join(columns)})")

    def arm(self, labels):
        """The runs of one arm — one label on every axis — across all its seeds."""
        for axis, label in labels.items():
            self.require_axis(axis)
            if label not in self.labels(axis):
                raise BriefError(f"{self.path}: axis '{axis}' has no label '{label}' "
                                 f"(its labels: {', '.join(self.labels(axis))})")
        open_axes = [a for a in self.axes if a not in labels]
        if open_axes:
            raise BriefError(
                f"{self.path}: nothing fixes axis '{open_axes[0]}', so runs from several arms would be "
                f"averaged together; name one label for it in `where` (one of: {', '.join(self.labels(open_axes[0]))})")
        return [r for r in self.rows if all(r[k] == v for k, v in labels.items())]

    def mean(self, labels, field):
        """(mean, min, max) over seeds, exactly as the report's Results table."""
        self.require_measure(field)
        return sweep.aggregate(self.arm(labels), field)

    def change(self, labels, field, baseline=None):
        """The change against the reference arm, as the report's comparison table.

        The baseline names some axes; the reference is the arm with the
        baseline's labels on those and this arm's own labels on the rest."""
        self.require_measure(field)
        baseline = baseline or self.baseline
        if not baseline:
            raise BriefError(f"{self.path}: its sweep names no baseline, so say which arm to compare "
                             f"with: baseline: {{{self.axes[0]}: {self.labels(self.axes[0])[0]}}}")
        return sweep.change(self.arm(labels), self.arm({**labels, **baseline}), field)

    def text(self):
        with open(os.path.join(self.dir, "report.md")) as f:
            return f.read()


class Reports:
    """Reports opened by a brief, each once, in the order first used."""

    def __init__(self):
        self.opened = {}

    def get(self, path):
        key = relative(resolve(path)).rstrip(os.sep)
        if key not in self.opened:
            self.opened[key] = Report(key)
        return self.opened[key]


def git(*args):
    result = subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""


def stamp(inputs):
    """The version and commit a brief was rendered from, and which of its inputs
    differ from the commit.

    Only the brief's own inputs are asked about, so an unrelated local change
    elsewhere in the tree does not mark every render as modified. An input
    outside the repository is never committed here, so it always counts."""
    commit = git("rev-parse", "HEAD")
    paths = sorted({os.path.abspath(resolve(p)) for p in inputs})
    inside = [relative(p) for p in paths if p == ROOT or p.startswith(ROOT + os.sep)]
    outside = [p for p in paths if not (p == ROOT or p.startswith(ROOT + os.sep))]
    status = git("status", "--porcelain", "--", *inside) if commit and inside else ""
    modified = {line[3:].strip() for line in status.splitlines() if line.strip()}
    return {"version": sweep.own_version() if commit else "", "commit": commit,
            "modified": sorted(modified) + outside}
