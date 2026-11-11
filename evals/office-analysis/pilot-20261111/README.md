# Exploratory content-only pilot, 2026-11-11

Four analytical cases were authored once per condition in fresh independent
sessions: main `7bbd84c`, previous `f3ec351`, candidate `2da9be1`. A candidate-only
wording-edit guard made 13 initial outputs. Two additional wording-edit input
packages were prepared but not run; they are not scored as failures or successes.

The initial wording-edit author returned the correct paragraph but reported
reading the shared analysis guide despite the entry's scope exclusion. Routing
was clarified at `2baa27c` to follow the requested operation rather than analytical
statements in the edited source. A fresh wording-edit follow-up returned a scoped
paragraph and reported reading the Office entry without the shared guide. That
is an author-reported trace, not instrumented loader verification. The analytical
guide itself did not change during this follow-up.

The 13 initial answers passed an independent instruction-blinded AI content review
against the frozen criteria. The operating and fixed-cost results were tied on
important work; launch and research differences were valid conditional choices.
This small pilot does **not** demonstrate a consistent comparative improvement.
It is not an expert-calibrated or production Okou evaluation and does not reverse
the user's prior finding about the previous version.

Raw reader-facing outputs are in `answers/`. `results.json` records exact skill
commits, input/answer hashes and the mapping from anonymous reviewer keys to
conditions. `review.json` preserves the anonymous review; its source locations
map to `../cases/<case>/`, and its answer keys map through `results.json`. The
wording-edit follow-up is identified separately from the initial comparison.

All authors inherited the parent session's model and reasoning settings with no
model override. The exact provider model ID was not independently read back.
Authors ran in separate directories on a shared host, with identical requests,
source-only factual restrictions and guidance-only skill snapshots. Input hashes
were checked after authoring. These checks do not establish which files were read.
No native files were generated or rendered. There were no independent author
repeats, no expert adjudication and no instrumented time/cost comparison.
