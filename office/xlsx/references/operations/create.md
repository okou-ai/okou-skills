# CREATE a workbook

Use for a new workbook; existing files use [EDIT](edit.md). Select the applicable
scenario and presentation from [the entry point](../../SKILL.md), respecting user
templates and house style. Set `SKILL_DIR` and `OFFICE` there.

## Plan meaning before mechanics

Define reading/editing tasks, sheet purposes, source locations, adjustable inputs
and calculation flow. Keep source-backed facts distinct from assumptions; retain
live formulas for derived outputs. Use the applicable finance guidance without
imposing financial styling on ordinary tables. Before populating imported values
or inputs, read [data/input contracts](../common/data-and-inputs.md) for types,
source ownership, validation and parameter-linked narrative. For reader-facing
comparisons, plan the question, ranges and chart space with
[analytical charts](../common/charts.md). These are author decisions, not CLI inference.

## Build with a suitable library

Prefer maintained high-level workbook objects (for example openpyxl) when they
can preserve required features. Reuse the working environment; install only
missing dependencies when permitted. The optional dependencies are in
`$SKILL_DIR/requirements-authoring.txt`. Do not rebuild an existing source through
a library that drops its features.

Before substantial formula authoring:

```bash
python3 "$OFFICE" preflight --format xlsx
```

This checks an independent live-formula control, not the candidate. Diagnose a
failed control before blaming workbook content; unavailable calculation cannot
be described as a checked, ready-to-use model. See [VALIDATE](validate.md).

Populate numeric inputs as numbers, rates as decimals and dates with date formats.
Assign semantic roles **and** display formats; a ratio formula alone does not
select percentage formatting. Set full-width headings, readable column widths,
heights for wrapped notes, chart space and a usable print area. Keep source tables
separate from reader-facing reports; do not compress everything into fewer sheets.

For explicitly author-selected finance defaults, use the existing
[authoring primitives](../implementation/authoring.md) directly or apply an explicit
plan to a separate output:

```bash
python3 "$OFFICE" style --input draft.xlsx --out styled.xlsx \
  --plan plan.json --use-finance-defaults
```

Use `style --help` for the supported plan contract; do not invent plan fields.
A JSON plan is optional: prefer direct primitive calls when shorter, not a plan
for every task. The flag is opt-in, not permission to restyle a supplied template.
The author selects ranges, roles, formats and geometry; the primitives neither
supply a business model nor evaluate formulas or guarantee layout quality.

## Calculate, view and revise

Save a complete draft early, then follow [VALIDATE](validate.md): recalculate a
copy, verify source-based results and relevant input propagation, export the
relevant sheets in an application and inspect actual pages. The wrapper has no
XLSX render/export command. Revise defects within this attempt.

Check conversion effects before selecting the delivery file. Reopen that exact
file in formula and cached-value views without saving it. Any later library save
can clear caches: recalculate and recheck afterward. Never synthesize caches or
replace live formulas with answers. Deliver only requested files, disclosing
unavailable checks and incomplete critical outputs.

## Package-level fallback

When necessary, use [OOXML details](../implementation/ooxml.md) and a fresh copy of
`$SKILL_DIR/templates/minimal_xlsx`; `xlsx_pack.py --help` owns packing parameters.
Keep worksheet parts, relationships, content types, string/style references and
element order consistent. Sheet count follows the task, not the starter package.
Well-formed XML and placeholder caches are not calculation or compatibility
passes; use the same VALIDATE workflow as library-built workbooks.
