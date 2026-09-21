# Corpus harness

```bash
mkdir -p /tmp/corpus && cd /tmp/corpus && python3 <repo>/extract-template/tests/gen_corpus.py   # 9 docx
soffice --headless --convert-to pdf --outdir . *.docx                                            # 9 PDFs
python3 <repo>/extract-template/tests/harness.py docx pdf                                        # both routes
```

`harness.py` runs each guide step by step on every corpus file, converts
`probe.md` with the delivered package's own command, renders it with
LibreOffice, runs `run_delivered.py` (layout gate) and `compare.py` (rendered
output against the source PDF: paper, columns, margins, first baseline, body
font, size, colour, line advance, paragraph gap, header and footer position,
heading set).

Needs pandoc on PATH, LibreOffice Writer, PyMuPDF and python-docx.
