# Scenario C: Applying Formatting / Templates

## Contents

- [When to Use](#when-to-use)
- [Workflow](#workflow)
- [What Gets Copied from Template](#what-gets-copied-from-template)
- [What Does NOT Get Copied](#what-does-not-get-copied)
- [Template Structure Analysis (REQUIRED)](#template-structure-analysis-required)
- [Style Mapping Strategy](#style-mapping-strategy)
- [Relationship ID Remapping](#relationship-id-remapping)
- [Common Pitfalls](#common-pitfalls)

## When to Use

Use Scenario C when:
- The user has an existing document and wants to apply a different visual style
- The user wants to rebrand a document (new fonts, colors, heading styles)
- The user provides a template DOCX and wants its look applied to a content document
- The user wants consistent formatting across multiple documents

Use B for a narrow content edit or simple placeholder fill, and A for new creation
without a structured template. New content placed into a supplied structured
template uses C-2 Base-Replace: preserve the template's structure, not its example
identities or findings.

---

## Workflow

Inventory each unchanged input **once**, without SDK/setup. Choose the necessary
scope/details up front and reuse these files for all zone, style and relationship
decisions below; no separate preview/analyze pass. For whole-template zone selection,
use `--full` (all body elements and complete text, not XML). Byte-preservation checks
need `--hash-parts` for the preserved base; omit it for metadata-only inspection:

```bash
# Overlay preserves source parts; Base-Replace preserves template parts.
# Put --hash-parts on the relevant base inventory (both only if both are compared).
python3 "$SKILL_DIR/scripts/docx_inspect.py" inventory source.docx --full --hash-parts > source.inventory.json
python3 "$SKILL_DIR/scripts/docx_inspect.py" inventory template.docx --full > template.inventory.json
# For Base-Replace, move --hash-parts from source to template in these commands.
```

1. Choose Overlay or Base-Replace using `body_elements` (zero-based indices and
   text), `sections`, `styles` and `used_styles` from these inventories. Default
   inventory is only the first 50 elements / 160 characters per preview; always
   check `body_coverage` and `text_truncated`. A range (`--start N --end M`) is an
   alternative to `--full`. Add `--xml` only for actual XML-level ambiguity/editing.
2. Map used source paragraph/character/table styles to template definitions;
   preserve required numbering, CJK fonts, fields and semantic emphasis.
3. **Overlay only**, when style IDs already match and replacement of whole style/
   numbering parts is safe, use the built CLI (runtime needed):
   `bash "$SKILL_DIR/scripts/docx.sh" apply-template --input source.docx --template template.docx --output result.docx`.
   Headers/footers require explicit `--apply-headers-footers`; the CLI does not
   implement a mapping plan or Base-Replace. For those, adapt
   [C# authoring](../implementation/authoring.md#structured-template-boundaries).
4. Validate: `bash "$SKILL_DIR/scripts/docx.sh" validate --input result.docx --business`.
5. Review: `bash "$SKILL_DIR/scripts/docx.sh" diff --before source.docx --after result.docx`.
   This is a coarse text/style-ID/count diff, not a preservation certificate.
   Inventory the result once with `--full --hash-parts` when checking untouched-part
   bytes; compare `parts[].sha256` against the saved base inventory (not ZIP sizes,
   and do not rerun the unchanged base). Use `--xml` only if XML detail is needed.
   Compare `relationships`/`relationship_references` for remapped IDs and existing targets,
   and text/zones against the authorized changes. External links are not fetched.
   Apply [affected visual checks](validate.md#rendering-and-delivery); never write
   over either input.

---

## What Gets Copied from Template

| Part | File | Description |
|------|------|-------------|
| Styles | `word/styles.xml` | All style definitions (paragraph, character, table, numbering) |
| Theme | `word/theme/theme1.xml` | Color scheme, font scheme, format scheme |
| Numbering | `word/numbering.xml` | List and numbering definitions |
| Headers | `word/header*.xml` | Header content and formatting |
| Footers | `word/footer*.xml` | Footer content and formatting |
| Section props | `w:sectPr` | Margins, page size, orientation, columns |

## What Does NOT Get Copied

| Part | Reason |
|------|--------|
| Document content | Paragraphs, tables, images stay from source |
| Comments | Belong to source document's review history |
| Tracked changes | Belong to source document's revision history |
| Custom XML parts | Application-specific data, not visual |
| Document properties | Title, author, dates belong to source |
| Glossary document | Template's building blocks are not transferred |

---

## Template Structure Analysis (REQUIRED)

Before choosing Overlay or Base-Replace, review the template inventory from the
workflow above. Do not repeat the same inspection at each step.

### Step 1: Count template paragraphs and identify structural zones

Use the saved `template.inventory.json` created with `--full`: `body_elements`
includes each direct body child (including tables and SDTs), its `index`, `text`,
`paragraph_count` and `table_count`. Counts describe stored XML, not rendered or
revision-accepted content. `sections[].properties` includes intermediate/final
section metadata; style records and per-part `used_styles` identify heading-equivalent
IDs even when numeric. XML is included only with `--xml`; full text alone usually
suffices to find zones.

Identify these zones in the template:
```
Zone A: Front matter (cover page, declaration, abstract, TOC)
        → KEEP structural containers/fields; replace supplied-content placeholders,
          example identities and findings as authorized; do not retain sample facts
Zone B: Example/placeholder body content ("第1章 XXX", sample paragraphs)
        → This is REPLACED with user's actual content
Zone C: Back matter (appendices, acknowledgments, blank pages)
        → KEEP required structure or remove as authorized; update sample content
          from supplied evidence rather than retaining example references/identities
Zone D: Final sectPr
        → ALWAYS kept from template
```

### Step 2: Find Zone B boundaries (replacement range)

Search the saved full inventory's body text for anchors marking the replacement
range. Inspect targeted body XML (`inventory --start N --end M --xml`) or the source
XML part only if the saved evidence leaves an actual ambiguity; do not repeat all scans:

**Start anchor patterns** (first paragraph of example body):
- "第1章", "第一章", "Chapter 1", "1 Introduction", "绪论"
- The first paragraph with a Heading1-equivalent style after TOC

**End anchor patterns** (last paragraph before back matter):
- "参考文献", "References", "致谢", "Acknowledgments"
- The last paragraph before appendices or final sectPr

```python
# Pseudocode for finding replacement range
for i, element in enumerate(template_body_elements):
    text = get_text(element)
    style = get_style(element)
    if style in heading1_styles and ("第1章" in text or "Chapter 1" in text):
        replace_start = i
    if "参考文献" in text or "References" in text:
        replace_end = i
        break
```

**CRITICAL**: Verify the range by printing what's inside:
```
Template elements [0..replace_start-1]: front matter (KEEP)
Template elements [replace_start..replace_end]: example content (REPLACE)
Template elements [replace_end+1..end]: back matter (KEEP)
```

If replace_start or replace_end cannot be found, DO NOT proceed. Ask the user to identify the replacement boundaries.

### Step 3: Decide Overlay vs Base-Replace

Now that you know the structure:

| Observation | Decision |
|-------------|----------|
| Template has ≤30 paragraphs, no cover/TOC | **C-1: Overlay** (pure style template) |
| Template has >100 paragraphs with cover/TOC/example sections | **C-2: Base-Replace** |
| Template paragraph count ≈ user document | **C-1: Overlay** (similar structure) |
| Template paragraph count >> user document (e.g., 263 vs 134) | **C-2: Base-Replace** |

### Step 4: For Base-Replace, execute the replacement

1. Load template as base (all files)
2. Extract user content elements using `list(body)` — NOT `findall('w:p')` (which misses tables)
3. Build new body: `template[0:replace_start] + cleaned_user_content + template[replace_end+1:]`
4. Apply style mapping to every paragraph
5. Clean direct formatting (see rules below)
6. Rebuild document.xml, keeping template's namespace declarations
7. Merge relationships (images + hyperlinks)
8. Write output using template as ZIP base

---

## Style Mapping Strategy

When template style names differ from source style names, a mapping is required. **This step is mandatory** — skipping it is the #1 cause of formatting failures in template application.

### Step 0: Reuse Both Inventories' Style Records (REQUIRED)

Compare `styles` and `used_styles` in the saved source/template inventories, not
another command. Every definition has `styleId`, display `name`, `type`, `basedOn`,
`default`; XML is opt-in with `--xml`. Per-part usage includes `pStyle`, `rStyle` and `tblStyle`.
For example, source `Heading1` / name `heading 1` / basedOn `Normal` can map to
template `1` / name `heading 1` / basedOn `a`. Check the full inheritance chain
and default styles, not only custom definitions or English `Heading*` IDs.

**Critical distinction**: `w:styleId` vs `w:name`:
```xml
<!-- styleId="1" but name="heading 1" -->
<w:style w:type="paragraph" w:styleId="1">
  <w:name w:val="heading 1"/>
  <w:basedOn w:val="a"/>
</w:style>
```

The `w:styleId` attribute is what `<w:pStyle w:val="..."/>` references. The `w:name` attribute is the human-readable display name. **They can be completely different.** Many CJK templates use numeric styleIds (`1`, `2`, `3`, `a`, `a0`) instead of English names.

### Tier 1: Exact StyleId Match
If source uses `Heading1` and template defines `Heading1` as a styleId, map directly. No action needed.

### Tier 2: Name-Based Match
If no exact styleId match, try matching by `w:name` attribute:
- Source `Heading1` (name="heading 1") → Template styleId `1` (name="heading 1")
- Match is case-insensitive on the name value

Within the same type, also try matching by:
- Built-in style ID (Word's internal ID, e.g., heading 1 = built-in ID 1)
- Style type (paragraph → paragraph, character → character, table → table)

### Tier 3: Manual Mapping
For renamed or custom styles, provide an explicit mapping:

```json
{
  "styleMap": {
    "Heading1": "1",
    "Heading2": "2",
    "Heading3": "3",
    "Heading4": "3",
    "Normal": "a",
    "BodyText": "a",
    "ListBullet": "a",
    "CompanyName": "Title",
    "OldTableStyle": "TableGrid"
  }
}
```

### Common Non-Standard StyleId Patterns

| Template Origin | StyleId Pattern | Example |
|----------------|-----------------|---------|
| Chinese Word (default) | Numeric/alphabetic | `1`, `2`, `3`, `a`, `a0` |
| English Word (default) | English names | `Heading1`, `Normal`, `Title` |
| Google Docs export | Prefixed | `Subtitle`, `NormalWeb` |
| WPS Office | Mixed | `1`, `Heading1`, custom names |
| Academic templates | Custom | `ThesisHeading1`, `ThesisBody` |

### Building the Mapping Table

Follow this algorithm:

1. **List source styleIds** from `used_styles["word/document.xml"]`, and from any
   copied header/note parts. Include paragraph, run and table styles; absent
   explicit style references use the applicable default style. No second ZIP scan.

2. **For each used style**, find the best match in template:
   - First try: exact styleId match
   - Second try: match by `w:name` value (case-insensitive)
   - Third try: match by style purpose (any heading → template's heading style)
   - Fallback: map to template's default paragraph style (usually `Normal` or `a`)

3. **Validate the mapping** — every source styleId must map to an existing template styleId:
   ```
   ✓ Heading1 → 1 (name match: "heading 1")
   ✓ Heading2 → 2 (name match: "heading 2")
   ✓ Normal   → a (name match: "Normal")
   ✗ CustomCallout → ??? (no match found, will fallback to 'a')
   ```

4. **Apply the mapping** when copying content — update every `<w:pStyle w:val="..."/>`:
   ```xml
   <!-- Source -->
   <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
   <!-- After mapping -->
   <w:pPr><w:pStyle w:val="1"/></w:pPr>
   ```

### Unmapped Styles
Styles in the source document that have no match in the template are logged as warnings:
```
WARNING: Style 'CustomCallout' has no mapping in template. Content will fall back to 'a' (Normal).
```

The content is preserved; only the style reference is updated to the template's default paragraph style.

### C-2 BASE-REPLACE: Additional StyleId Considerations

When using the template as a base document (C-2 strategy), the template's `styles.xml` is already in place. You must:

1. **Never copy source `styles.xml`** — the template's styles are the authority
2. **Map every content paragraph's pStyle** to the template's styleId before insertion
3. **Strip direct formatting selectively** (see detailed rules below) — let the template style control appearance
4. **Verify table styles** — if source tables use `TableGrid` but template defines it as `a3` or similar, remap `<w:tblStyle>` too
5. **Check character styles** — `rPr` inside runs may reference character styles like `Hyperlink` or `Strong` that have different IDs in the template

### Direct Formatting Cleanup Rules (Detailed)

When copying content from source to template, apply these rules to EACH paragraph and run:

**REMOVE from `<w:rPr>`:**
- `<w:rFonts w:ascii="..." w:hAnsi="..."/>` — Latin font overrides (EXCEPT: keep `w:eastAsia`)
- `<w:sz>`, `<w:szCs>` — font size (let style control)
- `<w:color>` — text color
- `<w:highlight>` — highlight color
- `<w:shd>` — shading
- `<w:b>`, `<w:i>` — bold/italic UNLESS the source style requires it (e.g., emphasis)
- `<w:u>` — underline
- `<w:spacing>` — character spacing

**KEEP in `<w:rPr>`:**
- `<w:rFonts w:eastAsia="宋体"/>` — CJK font declaration (MUST keep, or Chinese text renders wrong)
- `<w:rFonts w:eastAsia="华文中宋"/>` — same reason
- Anything inside `<w:drawing>` — image references (handle separately via rId remapping)

**REMOVE from `<w:pPr>`:**
- `<w:pBdr>` — paragraph borders
- `<w:shd>` — paragraph shading
- `<w:spacing>` — line/paragraph spacing (let style control)
- `<w:jc>` — justification (let style control)
- `<w:tabs>` — custom tab stops
- `<w:rPr>` inside pPr — default run formatting for the paragraph

**KEEP in `<w:pPr>`:**
- `<w:pStyle>` — style reference (after mapping to template's styleId)
- `<w:sectPr>` — section properties (if intentionally inserting section breaks)
- `<w:numPr>` — numbering reference (after mapping numId to template's numbering)

**Table cells (`<w:tc>`):**
Apply the same rPr/pPr cleanup to every paragraph inside every cell. Also:
- Keep `<w:tcPr>` structural properties (column span, row span, width)
- Remove `<w:tcPr><w:shd>` (cell shading — let table style control)

---

## Relationship ID Remapping

When copying parts (headers, footers, images) from the template into the source package, relationship IDs (`r:id`) may collide.

**Problem**:
- Source has `rId7` → `image1.png`
- Template has `rId7` → `header1.xml`
- Copying template's `rId7` overwrites source's image reference

**Solution**:
1. Reuse the inventories' per-source-part `relationships` and
   `relationship_references`; check existing IDs, internal targets and missing refs
2. Find the maximum numeric ID (e.g., `rId12`)
3. Remap all template relationship IDs starting from `rId13`
4. Update all references in copied parts to use new IDs

```xml
<!-- Template original -->
<Relationship Id="rId1" Type="...header" Target="header1.xml" />

<!-- After remapping into source package -->
<Relationship Id="rId13" Type="...header" Target="header1.xml" />

<!-- Update sectPr reference -->
<w:headerReference w:type="default" r:id="rId13" />
```

### Hyperlink Relationship Merging

When the source document contains external hyperlinks (e.g., URLs in references or footnotes), these are stored as relationships in `word/_rels/document.xml.rels`:

```xml
<Relationship Id="rId15" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink"
              Target="https://example.com/paper" TargetMode="External"/>
```

The corresponding text in document.xml references this rId:
```xml
<w:hyperlink r:id="rId15">
  <w:r><w:t>https://example.com/paper</w:t></w:r>
</w:hyperlink>
```

**Merging steps:**
1. Reuse `relationship_references` in the source inventory for copied hyperlinks
2. For each, find the corresponding per-part relationship in `relationships`
3. Check if template already has a relationship with the same Target URL
   - If yes: reuse the existing rId, update the hyperlink reference
   - If no: assign a new rId (starting from template's max rId + 1), add the relationship to template's rels, update the hyperlink reference
4. Also check for hyperlink relationships used in footnotes (`word/_rels/footnotes.xml.rels`) and endnotes

**Common mistake:** Copying hyperlink paragraphs without merging rels → hyperlinks silently break (clicking does nothing in Word).

---

## Common Pitfalls

### 1. Orphaned Numbering References

**Problem**: Source document uses `w:numId="5"` in list paragraphs, but after replacing `numbering.xml` with the template's version, numbering ID 5 doesn't exist.

**Symptom**: Lists appear as plain paragraphs (no bullets/numbers).

**Fix**:
- Map source numbering IDs to template numbering IDs
- Update all `w:numId` references in document content
- Or merge source numbering definitions into template's `numbering.xml`

### 2. Missing Theme Colors

**Problem**: Source document's styles reference theme colors (`w:themeColor="accent1"`) that have different values in the template's theme.

**Symptom**: Colors change unexpectedly (usually acceptable — this IS the point of re-theming). But if a style uses `w:color` with both `w:val` and `w:themeColor`, the theme color wins in Word.

**Fix**: Review color changes. If specific colors must be preserved, use explicit `w:val` without `w:themeColor`.

### 3. Section Property Conflicts

**Problem**: Source document has multiple sections (e.g., portrait + landscape pages), but the template assumes a single section.

**Symptom**: All sections get the same margins/orientation, breaking landscape pages.

**Fix**:
- Only apply template section properties to the final `w:sectPr` in `w:body`
- Preserve intermediate `w:sectPr` elements (inside `w:pPr`) from the source
- Or apply template properties to all sections but preserve orientation overrides

### 4. Embedded Font Conflicts

**Problem**: Template specifies fonts not available on the target system.

**Fix**: Either embed fonts in the DOCX (`word/fonts/`) or use web-safe alternatives:
- Calibri → available on Windows/Mac/Office online
- Arial → universal fallback
- Times New Roman → universal serif fallback

### 5. Broken Style Inheritance

**Problem**: Template has `Heading1` based on `Normal`, but after applying template, `Normal` has different properties, cascading unwanted changes to headings.

**Fix**: Verify the `w:basedOn` chain for all critical styles. Ensure base styles are also correctly transferred from template.
