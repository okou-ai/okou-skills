# What must survive in this document?

Both document branches answer these five questions before anything else, from
the rendered pages. The questions are independent: answer each one, and each
`yes` pastes its clause into the package, in question order. A document that
answers `no` to all five is the only one whose reusable asset is a style sheet.

## The questions

### 1. Is there wording that must survive word for word?

Clauses, statutory notices, warranties, formal wording whose exact words carry
obligation or meaning. The test: would restating a passage in different words
change what the document commits to?

Yes → name the passages, then paste:

````markdown
Reproduce these passages exactly: <where they are>. Never paraphrase,
summarise, renumber, or drop one. Where the source cites its own sections by
number, dropping one means renumbering the citations with it.
````

### 2. Does the page leave blanks?

A typographic gap: a run of underscores, a rule drawn under spaces, a bracketed
or parenthesised instruction, an initial line. A placeholder word that reads as
ordinary text — `Facilitator name` — is not a blank; it is content to replace.

Yes → list the blanks with the branch's `scripts/find_blanks.py`, strike what
the rendered pages do not show as a blank, and paste one row per field — one
field can print as two marks:

````markdown
| Blank | Holds |
|---|---|
| `<the blank as the page shows it>` | <what a new document puts there> |
````

### 3. Will the next instance use these same blocks?

Section headings, a fixed run of fields, the same few lines in the same places.
Ask what the *next* one is called: if it keeps these blocks, they are the shape;
if it picks new ones, they are the subject.

Yes → paste, in reading order:

````markdown
Keep these blocks and what each holds:

- <one line per block>
````

### 4. Is any list a different length every time?

Attendees, line items, jobs held, action items, exhibits.

Yes → name the lists, then paste:

````markdown
Repeat or drop a whole block of the same kind for: <the lists>. Never build one
from scratch and never let one fall back to a style default.
````

### 5. Is the page carried by artwork and placement?

An image doing the work, text set where the artwork leaves room, lines short
because they have to fit. A letterhead logo does not count; the artwork has to
be carrying the page.

Yes → paste:

````markdown
Keep the artwork and where each line sits. If a replacement no longer fits,
shorten the wording — never the type, the spacing, or the position.
````

## What to deliver

| | |
| --- | --- |
| Any question answered `yes` | Publish the source file, with the clauses above as the package body. A style sheet carries none of those. |
| All five answered `no` | Build the style sheet, `reference.docx`. |

The branch guide gives the packaging mechanics and nothing else; the clauses
are written here once so that a `.docx` and its PDF export get the same package.

## Where this is easy to get wrong

- **Placeholder text does not answer question 1 or 2 on its own.** Question 1 is
  about the words that stay; question 2 is about typographic gaps. A page can
  carry placeholders and answer `no` to both.
- **Question 1 is the expensive one to miss.** A package that does not name the
  binding wording invites a new instance to restate it in its own words. The
  other four cost a re-run.
- **Headings alone do not answer question 3.** They answer it only if the next
  instance keeps those same headings. Headings over prose the next instance
  writes at its own length — a report's Summary, Findings, Recommendations —
  answer `no`: a style sheet carries the headings, and the length is free.
- **Sparse pages are not slides.** A page can hold less text than a slide and
  still be a document; the dispatcher's rule about paper sizes applies here too.
