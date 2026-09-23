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

## 1.1.0 — unreleased

MINOR: sweeps added; every number already recorded is as it was.

- Two sweeps asking how much of what decay did came from knowing where people
  would walk: `foresight-with` (simlab-api 3.0.0) and `foresight-without`
  (simlab-api 4.0.0-dev, which protects a person along every tunnel they could
  reach), both on autoscaler 2.0.0. Their reports name this repository
  1.0.1-dev.1: they began before this section existed, so the label says
  patch where this says minor.
- Experiment 005 names its builds on its verdict, as the others do.
- A sweep can score every run for use cases (`"use_cases": [{"label", "kind",
  "params"}]`), recording each case's summary — decisions, share in time, never
  had it, unwinnable, latency and slack — under its label, as columns a report
  can show and compare. A sweep that scores none records what it always did.
- `use-cases-decay`: decay against the decisions it is for, on the calibrated
  days.
- A sweep can draw closure maps of every run (`"closures": [{"label",
  "params"}]`, simlab-api's use case 2), recording each map's summary under its
  label as columns a report can show and compare: the dangerous ground it
  closed, the ground it closed needlessly, how much of the mine it shuts, and
  how long after an event it covered all of it. Several maps of one run cost
  almost nothing, so one run can be read under several allowances and levels.
- `closure-map`: that map against pick error, on the calibrated day and the
  earthquake, with and without decay.
- Two sweeps over a mine that is worked (simlab-api's activity model):
  `activity-blasting` (night, day, spread through the night, one round a day)
  and `activity-shape` (2, 4 or 8 faces × mostly blasting, balanced, mostly
  working). Both are the calibrated day with its events moved to where mining
  puts them, not a new rate.

## 1.0.0 — 2026-09-22

The first versioned release. Reports and briefs made before it name this
repository's commit only; from here they name its version beside it, as they
do the services'.

- Experiments 001–006 and findings 001–006.
- Sweeps and their reports: cloud-caps, intent-modes, lookahead-uncertainty,
  mid-run-switch, pick-jitter, pre-location, promotion, scenario-shapes and
  workforce; and four sweeps of the autoscaler's own settings on the
  calibrated days — settings-capacity, settings-coldstart, settings-scale-down
  and settings-engine — with their reports, on autoscaler 2.0.0-dev.3 and
  simlab-api 3.0.0.
- A sweep can pin a service to a release (`"build": {"simlab-api": "v3.0.0"}`)
  and name its report's columns. A report names the version of each service
  and of this repository that produced it.
- Briefs rendered to PDF from the reports (`make pdf`), naming this
  repository's version and commit on every page.
- A sweep records this repository as it was when the sweep began, so a commit
  made while it runs is not credited with it; a reading in `sweeps/*.md` no
  longer marks a report modified.
- An experiment names the builds it ran on — each service's version and commit,
  and this repository's version — when it starts and on its verdict.
- `make version`, `make check` and `make release`, with the service
  repositories' version and release scripts; releases are cut from `master`.
