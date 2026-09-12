# 003 — Does the settings compare-and-swap hold under contention?

**Status:** no defect found. Kept as a standing check.

## The question

Settings are changed while the service runs, and the design makes three
promises about that:

1. A write carrying `expected_version` is a compare-and-swap, so two people
   tuning the same target cannot silently overwrite each other.
2. A reader never sees half of one edit and half of another — the store
   validates a whole candidate document and then swaps a pointer.
3. A rejected write leaves the running engine on exactly the settings it
   already had.

Each is easy to state and easy to believe. Concurrency is where beliefs like
these turn out to be wrong, and a unit test with one goroutine cannot tell.

## Method

- **Twenty editors, one version.** All read the same version, all write against
  it. Exactly one may win; the other nineteen must be refused as stale.
- **A paired write under a reader.** A writer repeatedly sets two fields whose
  values must stay in a fixed relation to each other, while a reader checks the
  relation on every read. Any other pairing is a document assembled from two
  versions.
- **A rejected write.** Send a document that fails validation and confirm the
  version does not move.

## Result

**No defect found.** All three promises held:

```
✓ exactly one writer won
✓ the other nineteen were refused as stale
✓ nobody got an unexpected status
✓ the version advanced exactly once
✓ no reader ever saw a half-applied edit
✓ a floor above the ceiling is refused
✓ the version did not move
```

## What writing it taught

The first version of this experiment reported a torn read that was not one. The
reader began before the paired writer's first request landed, so it observed a
perfectly consistent document left behind by the previous section and judged it
against an invariant that did not hold yet.

That is the characteristic failure of an experiment like this, and worth
stating plainly: **an experiment must establish its invariant before it starts
observing it**, or the first thing it reports is its own setup. The fix is the
explicit seeding write now at the top of that section.

The read count is modest — around a dozen reads against forty writes — so this
is evidence that the swap is not obviously broken, not a proof that it is
linearisable. Treat it accordingly.

## Running it

```bash
./run.sh
```

Needs Docker and Go, and the service repositories checked out alongside. Exits
non-zero if any check fails.
