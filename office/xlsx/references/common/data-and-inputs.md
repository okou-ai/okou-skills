# Source data and editable inputs

Use when importing data, creating an adjustable workbook or changing authorized
inputs. Preserve supplied templates and untouched data; reading or analyzing a
source is not permission to add validation, helper sheets or formatting to it.

## Establish the schema before writing

Reuse a confirmed source schema (sheet/header locations, relevant fields, grain,
units and periods); recheck affected fields when source, parsing or structure
changes, not a second full profile. Keep source records distinct from cleaned/
calculated outputs. For imports reconcile row counts and representative records;
for CSV/TSV confirm delimiter, encoding and locale, not just import success.

Choose types from field meaning, not appearance alone:

- Preserve identifiers, leading zeros and long account codes as text. A string
  that resembles a number or date is not automatically a quantity or date.
- Store amounts as numbers and rates as decimal fractions; assign display
  formats separately. Confirm decimal/thousands separators before conversion.
- Distinguish full dates, month selectors and text period labels. A date serial
  and a string such as `2026-12` are different inputs to formulas. Make dropdown
  values compatible with the receiving formulas; test a saved selection when
  application interaction is available.
- Keep missing, invalid, unavailable and zero states distinct. Report rejected
  conversions or missing records; do not silently drop them or replace them
  with zero to obtain a clean-looking total.

Inspect formulas/caches separately: missing or blank caches are unknown, not
zero. Values-only reads never calculate or overwrite formula sources. Use
[READ](../operations/read-analyze.md) for extraction/analysis, without input design.

## Only for authored/changed editable inputs and calculations

Give each material assumption one identifiable source cell or named range, with
its unit and source/default/illustrative status. Reference that location from the
calculations instead of scattering repeated business constants through formulas.
A fixed source assumption need not become a new user control merely to be
centralized. Do not turn retained history or every numeric cell into an input.

Use descriptive range names when they improve a complex model; short explicit
cell references are also valid. Check name scope, targets and dependencies after
structural edits. Consider tables, filters or other analytical objects only when
they help the requested task and the chosen tools can preserve them. The bundled
XML helpers do not promise complete pivot, slicer or connection support.

Keep summaries live. Text describing the current scenario must follow the inputs
or clearly identify the stated baseline; static source/default notes may remain
static. Check both the numbers and their interpretation after a driver changes.

## Only for authored/changed input contracts

For authored editable fields with a known domain, choose suitable type, allowed
values/range and blank policy. Do not invent business bounds absent from the
request or model specification. If a denominator can legitimately be zero,
define an appropriate undefined/not-applicable result; arbitrary zero or a
blanket `IFERROR(...,0)` can hide a broken model.

Use validation to guide entry, not as proof that stored data are correct. A list
object with its error alert disabled does not establish rejection of bad input.
For a new compatible openpyxl workbook, consult this optional recipe only when
needed: it encodes a planned whole-number range and enabled Stop alert, with
variables from the actual input plan:

```python
from openpyxl.worksheet.datavalidation import DataValidation

rule = DataValidation(
    type="whole", operator="between",
    formula1=str(lower_bound), formula2=str(upper_bound),
    allow_blank=False, showErrorMessage=True, errorStyle="stop",
)
rule.errorTitle = error_title
rule.error = error_message
ws.add_data_validation(rule)
rule.add(input_range)
```

Reopen the saved workbook and inspect the rule's target, bounds, blank policy and
alert settings. Where feasible, try representative allowed and rejected entries
and the actual dropdown in the intended application on a copy. A constructed
rule, XML check or numeric value written by a script is not a GUI entry test.
Pasted/programmatic values can still need independent validity checks. Preserve
existing controls during narrow edits instead of imposing new restrictions.

## Work in inspectable increments

Use the selected tool's installed help/API for uncertain operations. With large
writes, check one representative block and its types/formulas before expanding;
verify tool results and source coverage after structural changes. Choose batch
size for the tool and workload, not a fixed universal operation count.

Save pending authorized edits before another program reads them. A later save
can clear caches: apply the shared [VALIDATE impact matrix](../operations/validate.md#1-select-checks-by-impact)
to the exact revision, not an unconditional mutation/recalc/export sequence.
Authoring libraries and static previews do not prove engine execution.
