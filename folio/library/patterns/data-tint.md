---
id: data-tint
family: data
registers: [corporate, catalog]
loud: false
---
# Data on tint

> **Modified by Okou.** Adapted from Folio; [source and authorship](../INDEX.md#source-and-authorship).

**Use for:** Tables and charts that need a coherent visual family distinct from surrounding narrative.

**Composition**
- Place related data on a pale tinted panel; use a stronger colour band for one summary, not for every chart.
- Align chart titles, plot edges and table columns to shared guides. Keep units, dates and source notes close to their data.
- Reuse the same chart type for the same analytical question; choose bars for comparison and lines for change over time.

**Starting points**
- Use one main data colour, a neutral and a limited highlight. A lighter tint can mark context, but check that series remain distinguishable.
- Tables can start with a 0.8pt header rule and 0.25–0.5pt row rules; test thin strokes in the actual output.
- Right-align numeric columns and use tabular figures. Prefer whitespace to unnecessary vertical borders.
- Direct-label series when possible; do not encode meaning through colour alone. Check text and line contrast against the tint.

**Watch for:** Default multi-colour styling, unreadably faint axes, heavy boxes around every cell, or inconsistent scales across comparable charts.

**Construction:** SVG can retain crisp chart geometry; HTML tables preserve text structure. Verify labels, scale, clipping and source data after rendering.
