// Neutral PDF source: append your own content below.
// Compile with Typst; no colors, decoration, page numbers, or report outline.

#set page("us-letter", margin: (left: 108pt, right: 108pt, top: 65pt, bottom: 64pt))
#set text(font: ("Liberation Serif", "Noto Serif CJK SC"), size: 12pt,
  top-edge: .8em, bottom-edge: -.2em)
#set par(leading: 4pt, spacing: 8pt, justify: false, first-line-indent: 0pt)

#let doc-title(body) = block(above: 0pt, below: 14pt, sticky: true)[
  #set text(size: 18pt, weight: "bold")
  #set par(leading: 4pt)
  #body
]

#show heading: it => block(above: 16pt, below: 9pt, sticky: true)[
  #set text(size: 13pt, weight: "bold")
  #set par(leading: 4pt)
  #it.body
]

#show table: it => {
  set text(size: 11pt)
  set par(leading: 3pt, spacing: 0pt)
  it
}

#show figure.caption: it => {
  set text(size: 10pt)
  set par(leading: 3pt)
  it
}
