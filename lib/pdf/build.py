#!/usr/bin/env python3
"""Renders a brief — a written synthesis across reports — to PDF.

    build.py BRIEF.md OUT.pdf

Run it through `make pdf B=NAME`, which installs the pinned dependencies first.
briefs/README.md says how to write one.
"""

import os
import sys

# No __pycache__ beside lib/sweep.py and this package: nothing in this repository
# ignores it, and it is not source.
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from render import render  # noqa: E402
from sources import BriefError  # noqa: E402


def main(argv):
    if len(argv) != 3:
        sys.exit(__doc__.strip())
    brief, out = argv[1], argv[2]
    try:
        pages = render(brief, out)
    except BriefError as err:
        sys.exit(f"cannot render {brief}: {err}")
    print(f"wrote {out} ({pages} pages)")


if __name__ == "__main__":
    main(sys.argv)
