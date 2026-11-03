# OOXML implementation reference

Read only for direct package/XML changes. Use the selected business and
presentation rules to decide what to build; this reference covers how it is
encoded, not a second set of financial defaults.

## Package relationships

| Part | Responsibility |
| --- | --- |
| `[Content_Types].xml` | Content types of package parts |
| `_rels/.rels` | Root relationship to the workbook |
| `xl/workbook.xml` | Named sheets, defined names and calculation settings |
| `xl/_rels/workbook.xml.rels` | Relationship IDs to sheet, style and string parts |
| `xl/worksheets/*.xml` | Cells and worksheet-level features |
| `xl/styles.xml` | Shared font/fill/border/number-format/style definitions |
| `xl/sharedStrings.xml` | Optional shared text table; inline strings are also valid |

Resolve part targets relative to the relationship's owner; do not assume every
input file uses the starter's filenames or relationship IDs. Keep the sheet
list, relationship, actual part and content-type declaration synchronized when
adding sheets. Preserve unrelated charts, controls, objects and dependencies.

## Cells and formulas

| Value | XML |
| --- | --- |
| Number | `<c r="B2"><v>1000</v></c>` |
| Shared text (entry 0) | `<c r="A1" t="s"><v>0</v></c>` |
| Inline text | `<c r="A1" t="inlineStr"><is><t>Label</t></is></c>` |
| Boolean | `<c r="D1" t="b"><v>1</v></c>` |
| Formula, not yet recalculated | `<c r="B4"><f>SUM(B2:B3)</f><v/></c>` |
| Cached error | `<c r="B4" t="e"><f>B2/B3</f><v>#DIV/0!</v></c>` |

A formula's XML text has no leading `=`. Quote sheet names with spaces and
double embedded apostrophes, such as `'Q1 Data'!B5` or `'O''Brien'!B5`.
XML-escape `&` and `<` in text/formulas. Preserve meaningful whitespace with
`xml:space="preserve"` on text nodes. Rates use decimal values with a percentage
format; dates need the workbook's date-system basis and a suitable format.

Shared formulas have one primary `<f t="shared" ref="D2:D100" si="0">…</f>`
and consumers `<f t="shared" si="0"/>`. Review the primary and complete range,
not an apparently empty consumer. Preserve valid array/spill formula metadata.

For shared strings, preserve existing entry order. `uniqueCount` counts entries;
`count` counts total shared-string cell references across the workbook. Editing
one shared entry changes every referencing cell; append for a cell-local edit.

## Styles and display

A cell's `s` is a zero-based `cellXfs` index, not a color code. Its `xf` points
to fonts, fills, borders, alignment and number formats. Row/column styles,
theme/indexed colors and conditional formatting can also affect appearance.
Inspect the actual file rather than assuming a style number means "input".

Reuse definitions or append a new font/fill/border/format and `xf` combination;
update counts and apply the new index only to intended cells. Keep reserved
fills (`none`, `gray125`) and all existing indices stable. Custom number-format
IDs are unused values of at least 164; built-ins need no declaration.

Colors may use eight-digit ARGB (for example `FF0000FF` for blue), theme or
indexed definitions. Preserve valid existing encodings; do not treat `FF` as
an instruction to make text invisible. Use the financial layer's RGB roles
when applicable, not arbitrary palette colors.

Useful built-in number formats: `1` → `0`, `3` → `#,##0`, `4` → `#,##0.00`,
`9` → `0%`, `10` → `0.00%`, `14` → locale-sensitive short date. Inspect custom
formats by ID; they are not shared constants across workbooks.

Place `<cols>` before `<sheetData>` and row heights on `<row>`. Place frozen
panes inside `<sheetView>`. For example, freeze the first row with
`<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>`.
Apply full-range borders/fills without erasing cell-specific number formats.
