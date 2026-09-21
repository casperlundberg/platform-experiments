# Briefs

A brief is a written synthesis across reports — what the sweeps and experiments
found so far, for someone who has not read them — rendered to PDF.

```bash
make pdf B=2026-09-21-findings   # → out/briefs/2026-09-21-findings.pdf
make pdfs                        # every brief
make test-pdf                    # the renderer's own tests
```

The first run builds a venv of pinned packages under `out/` (a minute, once).
PDFs land in `out/`, which is not committed: the brief is the source, and the
same brief at the same commits renders to the same bytes.

## What a brief may say, and where its numbers come from

A report is evidence because its numbers are tied to the builds that produced
them. A brief keeps that tie by **quoting reports instead of retyping them**:
its figures and tables are drawn from `reports/NAME/` as the sweep wrote them,
through the same aggregation `lib/sweep.py` uses to print the report, and a test
(`test_brief.py`) holds every chartable mean and change to what its report
printed. A `runs.csv` that no longer matches the digest in its `provenance.json`
refuses to render.

Prose is the author's. Numbers written into the prose should come from the
report's reading or tables, and say which; the figures beside them keep the
prose honest.

## Writing one

Name it `YYYY-MM-DD-topic.md`, so briefs sort by when they were written and an
old one is never silently updated. Start with a YAML header:

```yaml
---
title: Ordering seismic processing by intent — findings to date
subtitle: One line on what is covered
author: A. Person
date: 2026-09-21
header: Findings to date     # running header on every page but the first; default: title
toc: true                    # a contents page; default: false
numbered: true               # number #/## sections; default: true
---
```

Then ordinary Markdown: headings, paragraphs, **bold**, *italic*, `code`,
lists, tables, block quotes (set as a tinted callout), code blocks, links (web
links stay clickable; repository-relative ones keep only their text), and
images standing alone in a paragraph (a numbered figure, captioned from the alt
text). Also:

- `# Heading {-}` leaves one heading unnumbered — a summary, an appendix.
- `Table: caption` in the paragraph directly after a table numbers and captions it.
- `<!-- pagebreak -->` starts a new page.

A character the fonts do not carry stops the render and names the line: a
dropped minus sign reverses a result, so nothing prints as a blank.

### `chart` — a figure from a report's runs

````markdown
```chart
source: reports/scenario-shapes      # a report directory
kind: dots                           # bars (default), dots or lines
x: shape                             # the axis laid out along the chart
series: intent                       # the axis to colour by (optional)
where: {intent: [off, "decay to its own level"]}   # a list picks and orders labels; one label fixes an axis
y:                                   # one panel per entry, side by side, each with its own scale
  - {measure: sla_breaches, label: Breaches per day, log: true}
  - {measure: ttl_exposing_mean_s, label: Seconds to locate an exposing event}
  - {measure: cloud_hours, label: Cloud hours vs no intent, change: true}
names: {off: no intent}              # display names for labels
colors: {"decay to its own level": 3}   # pin a categorical slot 1–8, 'neutral' or #rrggbb
caption: What the reader should see in it.
```
````

- Every point is one arm: each axis of the sweep must be laid out, coloured by,
  or fixed by `where`, or the chart refuses rather than average arms together.
- A measure is any column of `runs.csv`, shown as the **mean over seeds** with
  the range across seeds (off with `range: false`; off by default on lines).
- `change: true` shows the change against the report's baseline — seed totals,
  as the report's comparison table — and leaves out the reference itself.
  `baseline:` at the top level overrides the report's.
- `log: true` is for dots and lines; bars measure from zero and refuse it.
- The reference arm is drawn in neutral grey; other series take categorical
  slots in a fixed order. `ramp: true` colours ordered series (a lookahead, a
  pick error) from one hue, light to dark. Pin colours when the same arm
  appears in several figures, so it keeps its colour.
- `values: true` on a panel labels each mark; use it sparingly.
- `height:` sets the figure height in inches.

A figure that needs anything else — a scatter, a timeline, data from a single
run — is drawn by a script of its own, committed beside the brief, and included
as an image.

### `table` — a table lifted from a report

````markdown
```table
from: reports/intent-modes            # a report directory, or any .md file
section: Against off · estimate       # the heading the table sits under, exactly
rows: ["decay, restored exempt · estimate", "promote · estimate"]   # pick and order rows by first cell
columns: [Arm, Breaches, Cloud h]     # pick and order columns by header
rename: {"promote · estimate": "Promotion"}
caption: What the reader should take from it.
```
````

### `provenance` — the builds behind the numbers

````markdown
```provenance
```
````

Lists every report the brief draws on, with its run count, both services'
versions and commits, the commit that measured it, and its `runs.csv` digest.
Put it in an appendix; it is complete wherever it sits.

## The stamp

The first page says which platform-experiments commit the brief was rendered
from, and names any of its inputs — the brief, the reports it draws on, the
renderer — that differ from that commit. Commit the brief before rendering the
copy you send, and the stamp says so.
