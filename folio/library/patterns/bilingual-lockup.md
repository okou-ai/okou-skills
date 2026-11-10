---
id: bilingual-lockup
family: device
registers: [corporate, magazine, event, catalog]
loud: false
---
# Bilingual lockup

> **Modified by Okou.** Adapted from Folio; [source and authorship](../INDEX.md#source-and-authorship).

**Use for:** Two scripts or languages that should read as one coordinated heading.

**Composition**
- Decide language priority from the brief, not from the script. For a lead/support hierarchy, place a small kicker above or a gloss immediately below the main title.
- Start the supporting line around 35–50% of the lead's size, then adjust optically. For equal-status languages, use comparable visual weight with spacing or a rule to separate them.
- Share an alignment edge where reading directions permit; do not force mixed-direction text into a Latin-first structure.

**Type and language checks**
- Use Unicode fonts with the required glyphs and shaping support. Mark language and direction in HTML (`lang`, and `dir` where needed).
- Avoid tracking connected scripts as if they were Latin capitals. For Tamil, preserve natural shaping and allow enough leading for vowel signs.
- Compare actual letterforms, not nominal point sizes; scripts differ in apparent scale. Test diacritics and the longest approved wording.
- Use an approved translation or authoritative published text where applicable; do not invent a back-translation.

**Watch for:** Two unrelated titles competing for attention; clipped marks; inconsistent font pairings; accidental language hierarchy.

**Construction:** Keep each language in its own text span or block. Verify rendering, line breaks, text selection and font embedding in the final output.
