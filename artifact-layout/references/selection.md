# Choose a layout

Separate four decisions: visual theme, section grid, content component, and
reading sequence. They can be combined; a two-column grid is not a visual theme.

| Supplied material | Visual recipe | Grid and emphasis |
| --- | --- | --- |
| Research findings with prose and evidence | `editorial-research` | Flowing two-column analysis, a few large numbers, full-width evidence, quiet notes |
| Periodic business metrics and commentary | `executive-brief` | A metric strip, open single-column context, paired charts or modular summaries |
| Alternatives compared on common dimensions | `comparison-review` | A wide comparison table, main/sidebar explanations, paired evidence |

These are layout defaults, not analysis methods or required outlines. Omit
components without matching material. Retain the user's section order and
existing conclusions. Do not add numbers, rankings, quotations, or claims just
to fill a recipe.

## Themes

- **Editorial:** paper white, near-black ink, restrained blue, serif display.
- **Warm editorial:** cream paper, brown ink, terracotta accents.
- **Corporate:** white paper, blue emphasis, sans-serif display and body.
- **Mono:** grayscale, typography and rules carry hierarchy.

All use the same semantic tokens and components. Brand inputs may override
tokens; a user-supplied visual template takes priority over the defaults.
Use one theme throughout a document, with emphasis varying by content role.

These theme and recipe IDs are local values for `report.json`. They are not
resource-registry IDs for `okou generate --design-system` or `--template`;
select them in the content model. Explicitly selected external resources keep
their own identity and take priority over local defaults.

## Grids

- `single`: long prose, compact reports, and wide evidence.
- `two-column`: actual sequential text flow; block grouping preserves related
  material. On narrow screens it becomes one column. `span: "all"` bridges both
  columns and resumes the body flow afterward.
- `sidebar`: independent main and supporting content, not two continuous text
  columns. Mark supporting blocks `placement: "aside"`.
- `modular`: paired independent blocks. Use different emphasis and full-width
  evidence rather than equal cards for the entire document.

Avoid narrowing dense tables into body columns. Use a full-width block or an
additional section. Preserve body and table type sizes when content grows.

## Full vocabulary

[catalog.json](../assets/catalog.json) preserves the complete working taxonomy,
including bilingual names, definitions, use cases, cautions, prompt examples,
and 24 public source references. It is not an industry-standard exhaustive
classification or a measured popularity ranking. Original Chinese explanatory
text is retained as research data; English names support cross-language lookup.

| Group | Scope |
| --- | --- |
| S | Visual directions |
| L | Layouts and grids |
| T | Editorial components |
| N | Numbers and metrics |
| I | Image/text composition |
| C | Charts and compositions |
| B | Tables and matrices |
| D | Diagrams and models |
| R | Navigation and provenance |
| P | Narrative patterns |

Read only the relevant group or IDs through `catalog.py`. `rendering` identifies
a built-in component or marks the term reference-only. Advanced charts may be
authored externally and placed as figures; the package does not claim to
generate every chart in the vocabulary.
