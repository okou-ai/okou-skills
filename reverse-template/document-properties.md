# What must survive in this document?

Both document branches ask this before anything else, and they answer it here so
that one document does not get a different package for having arrived as a
`.docx` rather than a `.pdf`.

The questions below are independent: answer each one, and each `yes` adds its
clause to the package. A document that answers `no` to all of them is the only
one whose reusable asset is a style sheet.

## The questions

Read the rendered pages.

### 1. Is there wording that must survive word for word?

Clauses, statutory notices, warranties, formal wording whose exact words carry
obligation or meaning. The test: would restating a passage in different words
change what the document commits to?

→ Name those passages. The package says: reproduce them exactly, and never
paraphrase, summarise, renumber, or drop one.

### 2. Does the page leave blanks?

A typographic gap: a run of underscores, a rule drawn under spaces, a bracketed
or parenthesised instruction, an initial line. A placeholder word that reads as
ordinary text — `Facilitator name` — is not a blank; it is content to replace.

→ Give the package a table, one row per field: the blank as the page shows it,
and what a new document puts there. For a PDF, list them with
`pdf/scripts/find_blanks.py` rather than by eye.

### 3. Will the next instance use these same blocks?

Section headings, a fixed run of fields, the same few lines in the same places.
Ask what the *next* one is called: if it keeps these blocks, they are the shape;
if it picks new ones, they are the subject.

→ List the blocks in reading order and say what a new one puts in each.

### 4. Is any list a different length every time?

Attendees, line items, jobs held, action items, exhibits.

→ Name those lists. The package says to repeat or drop a whole block of the same
kind, never to build one from scratch or let it fall back to a style default.

### 5. Is the page carried by artwork and placement?

An image doing the work, text set where the artwork leaves room, lines short
because they have to fit. A letterhead logo does not count; the artwork has to
be carrying the page.

→ The package says: keep the artwork and where each line sits. If a replacement
no longer fits, shorten the wording — never the type, the spacing or the
position.

## What to deliver

| | |
| --- | --- |
| Any question answered `yes` | Publish the source file. A style sheet carries none of those. |
| All five answered `no` | Build the style sheet — the article route, `reference.docx`. |

The branch guide gives the packaging mechanics; the clauses above are its body.

## How this composes

Real documents answer several at once:

| Document | 1 wording | 2 blanks | 3 blocks | 4 lists | 5 artwork |
| --- | --- | --- | --- | --- | --- |
| Services agreement | yes | yes | yes | — | — |
| Meeting minutes | — | — | yes | yes | — |
| Party invitation | — | yes | yes | — | yes |
| Whitepaper | — | — | — | — | — |
| Certificate | yes | yes | yes | — | yes |
| Invoice | yes | yes | yes | yes | — |
| Résumé | — | — | yes | yes | — |

The whitepaper is the only style-sheet case. The certificate answers four at
once, which is why the questions are asked separately.

## Where this is easy to get wrong

- **Placeholder text does not answer question 1 or 2 on its own.** An agreement,
  an invitation and a set of minutes all carry placeholders. Question 1 is about
  the words that stay; question 2 is about typographic gaps.
- **Question 1 is the expensive one to miss.** A package that does not name the
  clauses invites a new instance to rewrite an indemnity in its own words. The
  others cost a re-run.
- **A heading hierarchy is not question 3.** A whitepaper has headings and
  answers `no`, because its next edition picks new ones.
- **Sparse pages are not slides.** A page can hold less text than a slide and
  still be a document; the dispatcher's rule about paper sizes applies here too.
