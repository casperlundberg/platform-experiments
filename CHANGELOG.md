# Changelog

Every release, newest first. `make release` will not tag a version without a
section here, so the tag message and this file always agree.

A number in a report comes from three places: the services that ran, named by
their own versions; the sweep's definition; and the code here that measures and
aggregates. This repository's version answers for the last two — **will the
same definition, on the same services, print the same numbers?**

- **MAJOR** — a number a report records can come out differently or mean
  something else: a measure or an aggregation redefined, a sweep's definition
  changed in place rather than added under a new name, or an experiment's check
  made to pass or fail on something else.
- **MINOR** — something added — an experiment, a sweep, a measure, a report
  column, a brief — and every number already recorded is as it was.
- **PATCH** — a fix that moves no number: wording, documentation, tooling.

## 1.0.0 — unreleased

The first versioned release. Reports and briefs made before it name this
repository's commit only; from here they name its version beside it, as they
do the services'.

- Experiments 001–006 and findings 001–006.
- Sweeps and their reports: cloud-caps, intent-modes, lookahead-uncertainty,
  mid-run-switch, pick-jitter, pre-location, promotion, scenario-shapes and
  workforce; and the definitions of four sweeps of the autoscaler's own
  settings on the calibrated days — capacity, coldstart, scale-down and the
  engine's dials.
- A sweep can pin a service to a release (`"build": {"simlab-api": "v3.0.0"}`)
  and name its report's columns. A report names the version of each service
  and of this repository that produced it.
- Briefs rendered to PDF from the reports (`make pdf`), naming this
  repository's version and commit on every page.
- An experiment names the builds it ran on — each service's version and commit,
  and this repository's version — when it starts and on its verdict.
- `make version`, `make check` and `make release`, with the service
  repositories' version and release scripts; releases are cut from `master`.
