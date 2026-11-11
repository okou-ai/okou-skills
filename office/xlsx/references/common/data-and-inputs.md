# Source data and editable inputs

Use when importing data, creating an adjustable workbook or changing authorized
inputs. Preserve supplied templates and untouched data; reading or analyzing a
source is not permission to add validation, helper sheets or formatting to it.

## Establish the schema before writing

Inspect sheet names, real header rows, used ranges, source record counts, units,
periods and relevant workbook features before selecting columns or coordinates.
Keep original records distinguishable from cleaned data and calculated outputs.
For CSV/TSV, confirm delimiter, encoding and locale; reconcile imported row counts
and representative records rather than trusting a successful import call.

After writing imported data, reopen the saved file and check the types in the
actual calculation ranges, including small adjustment tables. Reconcile their
amount totals and record counts to the source. Inspect the first and last data
rows against formula ranges; title/header rows can shift those coordinates.
Retain the source separately from any typed or cleaned representation.

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

Inspect formulas and existing caches separately when reading calculated files.
A values-only read does not evaluate formulas and must never overwrite the
formula source. Use [READ](../operations/read-analyze.md) for analysis boundaries.

## Make inputs and calculations maintainable

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

## Define and check input contracts

For authored editable fields with a known domain, choose suitable type, allowed
values/range and blank policy. Do not invent business bounds absent from the
request or model specification. If a denominator can legitimately be zero,
define an appropriate undefined/not-applicable result; arbitrary zero or a
blanket `IFERROR(...,0)` can hide a broken model.

Use validation to guide entry, not as proof that stored data are correct. A list
object with its error alert disabled does not establish rejection of bad input.
For a new compatible openpyxl workbook, this pattern encodes a planned whole-
number range and an enabled Stop alert; its variables come from the input plan:

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

Save pending edits before a different program reads the file. Recheck formulas,
references, caches and relevant features after that boundary; a library save may
clear application-generated caches. Follow [VALIDATE](../operations/validate.md)
for calculation, saved-file, visual and honest-delivery checks. Do not infer
spreadsheet-engine behavior from an authoring library or one preview renderer.
