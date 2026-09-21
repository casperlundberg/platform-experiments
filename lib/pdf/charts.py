"""Figures for a brief, drawn from a sweep's recorded runs.

A chart block names a report, the axis to lay out along the chart, the axis to
colour by, and the measures to show. Every value is the report's own mean over
seeds or its own change against the baseline (sources.Report), so a figure
restates numbers its report already prints and cannot quietly disagree with
them. A figure that needs anything else is drawn by a script of its own and
included as an image.
"""

import math
import textwrap
import warnings

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.ticker import FuncFormatter, LogLocator, MaxNLocator, NullFormatter, NullLocator  # noqa: E402

from sources import BriefError  # noqa: E402

# Categorical slots in a fixed order, never cycled: the order is what keeps
# neighbours distinguishable under colour-vision deficiency. The first three
# validate as every pair on white; a chart that needs more should facet.
CATEGORICAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
# The reference arm is there to be measured against, not looked at.
NEUTRAL = "#a3a19a"
# One hue, light to dark, for ordered series (a lookahead, a pick error). A
# rainbow would suggest categories; the lightest step still clears 2:1 on white.
RAMP = ["#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]
INK, SECONDARY, GRID, BASELINE = "#0b0b0b", "#52514e", "#e1e0d9", "#c3c2b7"

KINDS = ("bars", "dots", "lines")
KEYS = {"source", "kind", "x", "series", "where", "y", "baseline", "names", "colors", "ramp", "height", "caption",
        "xlabel"}
PANEL_KEYS = {"measure", "label", "change", "log", "range", "values"}

matplotlib.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 7.5,
    "axes.titlesize": 8,
    "axes.titlecolor": INK,
    "axes.labelcolor": SECONDARY,
    "xtick.color": SECONDARY,
    "ytick.color": SECONDARY,
    "text.color": INK,
    "legend.fontsize": 7.5,
})


def draw(spec, reports, path, width_in):
    """Draws a chart block to a PNG at path, width_in wide; returns its height in inches."""
    spec = dict(spec or {})
    unknown = set(spec) - KEYS
    if unknown:
        raise BriefError(f"chart: unknown key {', '.join(sorted(unknown))} (known: {', '.join(sorted(KEYS))})")
    for key in ("source", "x", "y"):
        if key not in spec:
            raise BriefError(f"chart: needs '{key}'")
    report = reports.get(spec["source"])
    kind = spec.get("kind", "bars")
    if kind not in KINDS:
        raise BriefError(f"chart: kind '{kind}' is not one of {', '.join(KINDS)}")

    x, series = spec["x"], spec.get("series")
    if series == x:
        raise BriefError(f"chart over {report.path}: x and series are both '{x}'")
    fixed, chosen = {}, {}
    for axis, value in (spec.get("where") or {}).items():
        report.require_axis(axis)
        if isinstance(value, list):
            if axis not in (x, series):
                raise BriefError(f"chart over {report.path}: where lists several labels for '{axis}', which the "
                                 f"chart neither lays out nor colours by, so their runs would be averaged; name one")
            chosen[axis] = [str(v) for v in value]
        else:
            fixed[axis] = str(value)
    xs = chosen.get(x) or report.labels(x)
    ss = (chosen.get(series) or report.labels(series)) if series else [None]
    baseline = spec.get("baseline") or report.baseline
    names = {str(k): str(v) for k, v in (spec.get("names") or {}).items()}
    panels = [panel(p, kind) for p in (spec["y"] if isinstance(spec["y"], list) else [spec["y"]])]
    if kind == "bars" and any(p["log"] for p in panels):
        raise BriefError(f"chart over {report.path}: a bar's length is its value, so bars need a zero baseline; "
                         f"use kind: dots for a log scale")

    def labels_for(xl, sl):
        labels = {**fixed, x: xl}
        if series:
            labels[series] = sl
        return labels

    def is_reference(labels):
        return bool(baseline) and {**labels, **baseline} == labels

    grids = []
    for p in panels:
        grid = {}
        for sl in ss:
            row = []
            for xl in xs:
                labels = labels_for(xl, sl)
                if p["change"]:
                    # The reference is zero against itself by definition; plotting it adds nothing.
                    value = None if is_reference(labels) else report.change(labels, p["measure"], baseline)
                    row.append(None if value is None else (value, value, value))
                else:
                    row.append(report.mean(labels, p["measure"]))
            grid[sl] = row
        grids.append(grid)

    references = {sl for sl in ss if series and all(is_reference(labels_for(xl, sl)) for xl in xs)}
    colours = colour_map(spec, ss, references)
    shown = [sl for sl in ss if any(v is not None for grid in grids for v in grid[sl])]

    height = spec.get("height") or default_height(kind, xs, ss, series)
    # Text is wrapped to what fits rather than left to collide or run off the
    # edge; the character widths are DejaVu's average at these sizes.
    panel_in = width_in / len(panels)
    title_chars = max(12, int((panel_in - 0.45) * 72 / (8 * 0.6)))
    tick_chars = max(4, int(panel_in / len(xs) * 72 / (7.5 * 0.6)) - 1)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        fig, axes = plt.subplots(1, len(panels), figsize=(width_in, height), layout="constrained", squeeze=False)
        for index, (ax, p, grid) in enumerate(zip(axes[0], panels, grids)):
            {"bars": bars, "dots": dots, "lines": lines}[kind](ax, p, grid, xs, ss, colours, names)
            ax.set_title(textwrap.fill(p["label"], title_chars), loc="left", pad=5)
            if kind != "dots":
                ax.set_xticks(range(len(xs)), [textwrap.fill(names.get(label, label), tick_chars) for label in xs])
                if spec.get("xlabel"):
                    ax.set_xlabel(spec["xlabel"], fontsize=7, color=SECONDARY, labelpad=4)
            ax.tick_params(length=0, pad=3)
            for spine in ax.spines.values():
                spine.set_visible(False)
            if kind == "dots" and index > 0:
                ax.tick_params(labelleft=False)
        if series and len(shown) > 1:
            fig.legend(handles=[handle(kind, colours[sl]) for sl in shown],
                       labels=[names.get(sl, sl) for sl in shown], loc="outside upper left",
                       ncol=min(len(shown), 4), frameon=False, handlelength=1.2, columnspacing=1.6)
        fig.savefig(path, dpi=300, facecolor="white", metadata={"Software": None})
        plt.close(fig)
    missing = [str(w.message) for w in caught if "missing from" in str(w.message)]
    if missing:
        raise BriefError(f"chart over {report.path}: {missing[0]}")
    return height


def panel(p, kind):
    if isinstance(p, str):
        p = {"measure": p}
    unknown = set(p) - PANEL_KEYS
    if unknown or "measure" not in p:
        raise BriefError(f"chart: a y panel takes {', '.join(sorted(PANEL_KEYS))} and needs 'measure'; got {p}")
    change = bool(p.get("change"))
    # Ranges across seeds are drawn by default, except on lines, where several
    # series' ranges stack at one x and hide each other.
    shown = not change and kind != "lines"
    return {"measure": p["measure"], "label": p.get("label", p["measure"]), "change": change,
            "log": bool(p.get("log")), "range": bool(p.get("range", shown)), "values": bool(p.get("values"))}


def colour_map(spec, labels, references):
    pinned = {str(k): v for k, v in (spec.get("colors") or {}).items()}
    if spec.get("ramp"):
        n = len(labels)
        steps = [RAMP[round(2 + i * (len(RAMP) - 3) / max(n - 1, 1))] for i in range(n)]
        out = dict(zip(labels, steps))
    else:
        out, slot = {}, 0
        for label in labels:
            if label in references:
                out[label] = NEUTRAL
                continue
            if label in pinned:
                continue
            if slot >= len(CATEGORICAL):
                raise BriefError(f"chart: more than {len(CATEGORICAL)} series; facet it rather than invent colours")
            out[label] = CATEGORICAL[slot]
            slot += 1
    for label, value in pinned.items():
        out[label] = colour(value)
    return out


def colour(value):
    if isinstance(value, int) and 1 <= value <= len(CATEGORICAL):
        return CATEGORICAL[value - 1]
    if value == "neutral":
        return NEUTRAL
    if isinstance(value, str) and value.startswith("#") and len(value) == 7:
        return value
    raise BriefError(f"chart: colour {value!r} is not a slot 1–{len(CATEGORICAL)}, 'neutral' or #rrggbb")


def default_height(kind, xs, ss, series):
    legend = 0.3 if series and len(ss) > 1 else 0
    if kind == "dots":
        return round(0.45 + legend + len(xs) * max(0.3, 0.15 * len(ss)), 2)
    return 2.3 + legend


def handle(kind, colour):
    if kind == "bars":
        return Patch(facecolor=colour)
    return Line2D([0], [0], color=colour if kind == "lines" else "none", linewidth=1.6, marker="o",
                  markersize=5.5, markerfacecolor=colour, markeredgecolor="white", markeredgewidth=1)


def bars(ax, p, grid, xs, ss, colours, names):
    n = len(ss)
    width = min(0.76 / n, 0.26)
    for j, sl in enumerate(ss):
        offset = (j - (n - 1) / 2) * width
        for i, v in enumerate(grid[sl]):
            if v is None:
                continue
            value, low, high = v
            # 86 % of the slot: what is left is the surface gap between neighbours.
            ax.bar(i + offset, value, width=width * 0.86, color=colours[sl], zorder=2)
            if p["range"] and low != high:
                ax.plot([i + offset] * 2, [low, high], color=SECONDARY, lw=0.7, zorder=3, solid_capstyle="butt")
            if p["values"]:
                ax.annotate(number(value, p), (i + offset, value), xytext=(0, 2 if value >= 0 else -2),
                            textcoords="offset points", ha="center", va="bottom" if value >= 0 else "top",
                            fontsize=6, color=SECONDARY)
    ax.axhline(0, color=BASELINE, lw=0.8, zorder=1)
    ax.set_xlim(-0.5, len(xs) - 0.5)
    ax.grid(axis="y", color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    scale(ax, "y", p)
    if p["values"]:
        ax.margins(y=0.12)


def dots(ax, p, grid, xs, ss, colours, names):
    n = len(ss)
    step = 0.2 if n > 1 else 0
    for j, sl in enumerate(ss):
        offset = (j - (n - 1) / 2) * step
        for i, v in enumerate(grid[sl]):
            if v is None:
                continue
            value, low, high = v
            y = i + offset
            if p["range"] and low != high:
                ax.plot([low, high], [y, y], color=colours[sl], lw=1.1, alpha=0.45, solid_capstyle="butt", zorder=2)
            ax.plot([value], [y], "o", color=colours[sl], markersize=5.5, markeredgecolor="white",
                    markeredgewidth=1, zorder=3)
            if p["values"]:
                ax.annotate(number(value, p), (value, y), xytext=(5, 0), textcoords="offset points",
                            va="center", fontsize=6.5, color=SECONDARY)
    ax.set_yticks(range(len(xs)), [names.get(label, label) for label in xs])
    ax.set_ylim(len(xs) - 0.5, -0.5)
    ax.grid(axis="x", color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    if p["change"]:
        ax.axvline(0, color=BASELINE, lw=0.8, zorder=1)
    scale(ax, "x", p)


def lines(ax, p, grid, xs, ss, colours, names):
    for sl in ss:
        points = [(i, v) for i, v in enumerate(grid[sl]) if v is not None]
        if not points:
            continue
        xi, values = [i for i, _ in points], [v[0] for _, v in points]
        ax.plot(xi, values, color=colours[sl], lw=1.6, solid_joinstyle="round", solid_capstyle="round", zorder=2)
        ax.plot(xi, values, "o", color=colours[sl], markersize=5, markeredgecolor="white", markeredgewidth=1, zorder=3)
        if p["range"]:
            for i, (value, low, high) in points:
                if low != high:
                    ax.plot([i, i], [low, high], color=colours[sl], lw=1, alpha=0.45, zorder=1)
        if p["values"]:
            ax.annotate(number(values[-1], p), (xi[-1], values[-1]), xytext=(5, 0), textcoords="offset points",
                        va="center", fontsize=6.5, color=SECONDARY)
    ax.set_xlim(-0.3, len(xs) - 0.7 if len(xs) > 1 else 0.3)
    ax.grid(axis="y", color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    if p["change"]:
        ax.axhline(0, color=BASELINE, lw=0.8, zorder=1)
    scale(ax, "y", p)


def scale(ax, which, p):
    axis = ax.xaxis if which == "x" else ax.yaxis
    if p["log"]:
        (ax.set_xscale if which == "x" else ax.set_yscale)("log")
        low, high = ax.dataLim.intervalx if which == "x" else ax.dataLim.intervaly
        decades = math.log10(high / low) if low > 0 and high > low else 0
        # Enough ticks to read a value off, and never so many that labels collide.
        subs = (1, 2, 5) if decades < 1.2 else (1, 3) if decades < 2.2 else (1,)
        axis.set_major_locator(LogLocator(subs=subs))
        axis.set_minor_locator(NullLocator())
        axis.set_minor_formatter(NullFormatter())
    else:
        axis.set_major_locator(MaxNLocator(nbins=5, steps=[1, 2, 2.5, 5, 10]))
    axis.set_major_formatter(FuncFormatter(lambda v, _: number(v, p)))


def number(value, p):
    if p["change"]:
        text = "0 %" if round(value * 100) == 0 else f"{value * 100:+.0f} %"
    elif value == 0:
        text = "0"
    elif abs(value) >= 100 or float(value).is_integer():
        text = f"{value:,.0f}"
    elif abs(value) >= 1:
        text = f"{value:,.1f}"
    else:
        text = f"{value:g}"
    return text.replace("-", "−")
