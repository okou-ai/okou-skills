# Office mechanical tools

Self-contained entry point: `python /absolute/path/to/office/scripts/office.py --help`.
No AI recursion, model selection, installation, agents or services are invoked.
Use the interpreter containing the selected format's dependencies; shell pipelines
inherit that interpreter's `bin` directory. Existing format-specific scripts remain usable.

```bash
python office/scripts/office.py list
python office/scripts/office.py style --help
python office/scripts/office.py tool-help --tool xlsx-formulas
```

`list` discovers actual executable paths and their limited scopes. Executions,
including argument errors, emit one JSON receipt on stdout. `--help` emits ordinary
help. Exit codes: 0 = requested mechanical steps succeeded, 1 = failure/check
findings, 2 = detected unavailable dependency. A runtime dependency may fail with
1 instead of 2; neither is a pass. Receipts preserve per-step argv, exit status,
stdout/stderr, elapsed time and artifact hashes for command audit; a child JSON
result is also exposed as `result`. Retain failed receipts alongside later rechecks.
Receipts are working evidence, not mandatory user attachments.

## Implemented paths

| Command | Reused implementation | Boundary |
|---|---|---|
| `preflight` | DOCX env check, Calc empty-cache control, PDF pipeline check | Tests environment/control, never candidate correctness |
| `create` | DOCX generic style defaults or PDF palette/cover/body/merge | Explicit content JSON required; supplied template/custom styling uses its format route |
| `style` | `xlsx_authoring.py`'s four existing primitives | Explicit finance-default opt-in and operation plan; simple XLSX only; no inferred roles/formulas |
| `validate` | DOCX SDK validator; XLSX formula scan + optional style audit; PDF `pdfinfo` | Separate scopes, not a general QA or business approval |
| `recalc` | Independent Calc control → candidate copy conversion → cache readback → static scan | Requires retained formula addresses and valid caches; expected results/input propagation still author-checked |
| `render` | Writer DOCX→PDF; Poppler PDF→PNG | No native XLSX export, image review or standards certification |

The author retains business judgment, fact boundaries, input semantics and final
usability. Requirements/templates override defaults. Never impose finance defaults
on ordinary tables or silently replace supplied styles. A library style save can
clear formula caches; recalculate and recheck the exact final file afterward.

Application paths use inspected private copies and new isolated profiles with
macros disabled and links not updated. Active/update-bearing OOXML is refused
conservatively; ordinary hyperlinks are allowed but not followed. These gates are
not an antivirus or network sandbox. Advanced/unsupported packages require the
format's preservation-aware route, not bypassing the gate. Inputs and existing
outputs (including symlinks) are never overwritten. No success is inferred from
an absent dependency, an empty output, a version probe or copied formula caches.
A computed empty string (`t="str"` with an existing empty `<v/>`) is a valid cache;
an absent cache or empty numeric cache is not. Automatic IMAGE/CUBE and selected
other external-data functions (including `_xlfn` forms) are conservatively refused;
NO_UPDATE is not network isolation or an exhaustive security proof.

For an authorized local runtime, `preflight`, `recalc` and `render` accept
`--soffice /absolute/path/to/soffice` (or `OFFICE_SOFFICE`); invalid overrides fail
without fallback. `TMPDIR` selects temporary storage. No workspace-private runtime
path is built into the skill.

## Tested examples / repeatable controls

With the format dependencies in your chosen interpreter:

```bash
python -m unittest discover -s office/scripts/tests -v
python office/scripts/smoke.py --out /tmp/office-control-NEW
# Optional actual PDF metadata/raster control (ReportLab + Poppler):
python office/scripts/smoke.py --out /tmp/office-pdf-control-NEW --with-pdf
# Optional actual Calc control/candidate path; nonzero if Calc is unavailable:
python office/scripts/smoke.py --out /tmp/office-calc-control-NEW --with-calc
```

Use a fresh `--out` each time. The smoke fixture contains only 19 + 23 and no
macros/business findings. It exercises explicit primitive reuse, source
preservation, formula/style scans and optional real application paths, writing
commands and receipts under that directory. Fake-runner unit tests cover failure
handling, safety boundaries and rejecting no-output/copied-cache calculations;
they are not evidence that the installed Office engine works. Run the actual
controls in the current environment and retain their receipts and limitations.
