# Choose the document's reuse scope

Read a few representative rendered pages and their content, including a body
page rather than only the cover or contents. Use the user's intended reuse to
choose in the order below; look at more pages if the scope is unclear. Make
this judgment directly. No classification script is needed.

| What carries over | Reuse scope | Package |
| --- | --- | --- |
| The fixed document; only designated slots may be filled | **Slot filling** | Original template, slot map and filling instructions |
| The content organization, presentation format and way of writing; the content is rewritten | **Structure and expression reuse** | Source example, structure and writing rules, and necessary layout assets |
| The visual formatting; content, organization and wording follow the new task | **Style extraction** | `reference.docx`, formatting instructions and necessary visual assets |

Choose by what the next document must retain, not by its name or file format.
A report can preserve its section order and writing conventions, or supply
only a visual style. Its DOCX and PDF export have the same reuse scope.

## Write the package for the selected scope

Write a loadable `SKILL.md` with `name` and `description` frontmatter. Its
description should identify the template and the operation it supports. Give
it concrete instructions for this document and link to the files it uses.
Include those files in the package; a catalog preview is not a package asset.

Classification ends here. The generated skill performs the selected operation
directly. Do not copy this decision table, unused routes or a collection of
conditional clauses into it.

### Slot filling

Keep the original as the working template. Map each slot to its location,
meaning and filling format. A slot may span several text runs; fixed labels
and surrounding prose are not slots.

Instruct the skill to fill a copy of the template. All text outside the slots,
artwork, layout and formatting stay unchanged. Do not add or remove sections,
rewrite fixed text or shrink the type to fit a value. Identify missing values
or values that will not fit without inventing or truncating them.

### Structure and expression reuse

Keep the source as an example and, where editable, a starting document.
Extract the rules a new instance needs: the purpose and order of its parts,
how information is presented, typical phrasing, tone and level of detail.
Use short examples from the source where they clarify a writing rule.

Say which content is rewritten, which wording stays fixed, and which items or
sections may repeat, be omitted or grow. Instruct the skill to compose new
content using these rules and preserve the corresponding formatting. Package
any artwork or other layout resources needed to do so. A list of blocks or
editable runs alone does not capture the expression rules.

### Style extraction

Extract paper size, margins, typography, colours, spacing and heading-level
formatting. The new task determines the subject, section organization,
wording and length. Do not carry over the source's section titles, fixed body
text or writing conventions as requirements.

The branch's style tools produce `reference.docx` and formatting instructions.
They also keep the source for visual comparison and rebuilding the styles;
that copy is not a content model. Retain any reusable visual assets needed
beyond the style file.

The DOCX and PDF guides specify how to build, verify and publish each package.
