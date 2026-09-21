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

## Document fidelity regressions

From the repository root:

```bash
python3 -m pip install --break-system-packages pymupdf python-docx pillow
python3 -m unittest discover -s extract-template/tests -p 'test_document_fidelity.py' -v
```

Also requires Node and Pandoc on PATH. The shared document renderer ensures
LibreOffice Writer and Poppler are available. Fixtures are generated in a
temporary directory; no user attachments are needed.

Covers flattened Word content controls, proportional portrait and mixed-size PDF
pages, native PDF forms, body and section selection, inherited frames and footers,
split text and field addresses, linked placeholders, and rendered probe failures.
After analyzer or builder changes, run both corpus routes above as well.
