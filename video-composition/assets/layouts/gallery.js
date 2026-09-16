const groups = [
  ["Orientation and closure", [
    ["orientation/headline-cover", "Cover", "titlecard-lockup"],
    ["orientation/section-pivot", "Section Pivot", "titlecard-calm"],
    ["orientation/briefing-map", "Briefing Map", "grid-card-assemble + line-by-line-slide · adapted"],
    ["orientation/public-action-close", "Public Action Close", "cta-close + line-by-line-slide · adapted"],
  ]],
  ["Text and evidence", [
    ["text/bullet-hierarchy", "Bullet Hierarchy", "line-by-line-slide + inline-highlight"],
    ["text/action-checklist", "Action Checklist", "grid-card-assemble · adapted"],
    ["text/claim-support", "Claim Support", "line-by-line-slide + inline-highlight"],
    ["text/two-column-argument", "Two Column Argument", "split-tilt-cards · adapted"],
    ["text/three-fact-columns", "Three Fact Columns", "grid-card-assemble"],
    ["text/document-excerpt", "Document Excerpt", "line-by-line-slide + inline-highlight"],
    ["text/source-quote", "Source Quote", "testimonial-proof-card"],
  ]],
  ["Metrics and charts", [
    ["data/single-stat", "Single Stat", "conic-progress-ring + number-pop-in · adapted"],
    ["data/kpi-row", "KPI Row", "grid-card-assemble"],
    ["data/kpi-grid", "KPI Grid", "grid-card-assemble"],
    ["data/ranked-bars", "Ranked Bars", "chart-story · adapted"],
    ["data/time-series", "Time Series", "mk-line-graph"],
    ["data/share-ring", "Share Ring", "conic-progress-ring · adapted"],
    ["data/scenario-range", "Scenario Range", "chart-story"],
    ["data/data-table", "Data Table", "grid-card-assemble + inline-highlight · adapted"],
  ]],
  ["Comparison and decision", [
    ["comparison/balanced-split", "Balanced Split", "split-tilt-cards · adapted"],
    ["comparison/before-after", "Before and After", "before-after-wipe · adapted"],
    ["comparison/benefit-risk", "Benefit and Risk", "split-tilt-cards · adapted"],
    ["comparison/option-matrix", "Option Matrix", "grid-card-assemble + state-chip-rail · adapted"],
    ["comparison/threshold-decision", "Threshold Decision", "state-chip-rail + number-pop-in · adapted"],
  ]],
  ["Time and process", [
    ["time/ordered-steps", "Ordered Steps", "tracing-beam + grid-card-assemble · adapted"],
    ["time/milestone-timeline", "Milestone Timeline", "beat-timeline · adapted"],
    ["time/phased-roadmap", "Phased Roadmap", "state-chip-rail + grid-card-assemble · adapted"],
    ["time/rollout-lanes", "Rollout Lanes", "beat-timeline + grid-card-assemble · adapted"],
    ["time/deadline-countdown", "Deadline Countdown", "titlecard-lockup + grid-card-assemble · adapted"],
    ["time/handoff-flow", "Handoff Flow", "tracing-beam · adapted"],
  ]],
  ["Systems and relationships", [
    ["system/hub-spoke", "Hub and Spoke", "constellation-hub"],
    ["system/dependency-network", "Dependency Network", "constellation-hub + tracing-beam · adapted"],
    ["system/decision-flow", "Decision Flow", "tracing-beam + state-chip-rail · adapted"],
    ["system/layered-system", "Layered System", "grid-card-assemble"],
  ]],
  ["Geography and media", [
    ["media/regional-map", "Regional Map", "us-map"],
    ["media/flow-map", "Flow Map", "us-map-flow"],
    ["media/media-left", "Media Left", "particle-image-reveal + line-by-line-slide · adapted"],
    ["media/media-right", "Media Right", "screen-flow-carousel + line-by-line-slide · adapted"],
    ["media/evidence-grid", "Evidence Grid", "screen-flow-carousel + grid-card-assemble · adapted"],
    ["media/evidence-hero", "Evidence Hero", "particle-image-reveal + inline-highlight · adapted"],
  ]],
];

const palettes = {
  "navy-cobalt": {
    label: "AUTHORITY BROADCAST",
    description: "The same 40 layouts rendered with the navy field and white information token collection.",
  },
  "monumental-minimal": {
    label: "MONUMENTAL MINIMAL",
    description: "The same 40 layouts rendered with the white field and navy-blue information token collection.",
  },
  "black-gold": {
    label: "BLACK GOLD",
    description: "The same 40 layouts rendered with the black field and restrained gold information token collection.",
  },
  "obsidian-champagne": {
    label: "OBSIDIAN CHAMPAGNE",
    description: "The same 40 layouts rendered with a near-black field, bone-white information, steel accents, and champagne signals.",
  },
  "petrol-brass": {
    label: "PETROL BRASS",
    description: "The same 40 layouts rendered with a deep petrol field, warm information, mineral accents, and restrained brass signals.",
  },
  "parchment-oxblood": {
    label: "PARCHMENT OXBLOOD",
    description: "The same 40 layouts rendered with a warm parchment field, carbon information, oxblood accents, and aged-brass signals.",
  },
  "porcelain-carbon": {
    label: "PORCELAIN CARBON",
    description: "The same 40 layouts rendered with a porcelain field, carbon information, blue-grey accents, and umber signals.",
  },
};

const gallery = document.querySelector("#gallery");
for (const [groupName, items] of groups) {
  const section = document.createElement("section");
  section.className = "family";
  section.innerHTML = `<header class="family-head"><p>${groupName}</p><span>${items.length} proofs</span></header><div class="grid"></div>`;
  const grid = section.querySelector(".grid");
  for (const [id, label, registryItem] of items) {
    const stem = id.replace("/", "--");
    const article = document.createElement("article");
    article.className = "card";
    article.innerHTML = `<a class="preview" data-preview-stem="${stem}" href="preview/${stem}.png"><img src="preview/${stem}.png" alt="${label} official HyperFrames render proof"></a><div class="copy"><h2>${label}</h2><p>${id}</p><span>HyperFrames · ${registryItem}</span><a href="source/${stem}.html">Open executable starter</a></div>`;
    grid.append(article);
  }
  gallery.append(section);
}

function applyPalette(name, updateUrl = true) {
  const palette = palettes[name] || palettes["navy-cobalt"];
  const selected = palettes[name] ? name : "navy-cobalt";
  document.documentElement.dataset.colorSystem = selected;
  document.querySelector("#palette-eyebrow").textContent = `${palette.label} · OFFICIAL HYPERFRAMES PROOFS`;
  document.querySelector("#palette-description").textContent = palette.description;
  // One sheet serves every palette: the forty layouts are identical apart from colour,
  // and the page itself recolours live from color-system.css.
  // Layout geometry is identical across palettes, so one proof set serves them all.
  // The palette switch re-themes the page itself and swaps the contact sheet.
  for (const button of document.querySelectorAll("[data-palette]")) {
    button.setAttribute("aria-pressed", String(button.dataset.palette === selected));
  }
  if (updateUrl) {
    const url = new URL(window.location.href);
    url.searchParams.set("palette", selected);
    history.replaceState({}, "", url);
  }
}

for (const button of document.querySelectorAll("[data-palette]")) {
  button.addEventListener("click", () => applyPalette(button.dataset.palette));
}
applyPalette(new URLSearchParams(window.location.search).get("palette"), false);
