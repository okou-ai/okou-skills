# PDF environments and stable entry points

Set `SKILL_DIR` to the directory containing the PDF `SKILL.md`, not this guide.
Reuse a working environment and install missing dependencies only when allowed.

For the cover/body pipeline, run
`bash "$SKILL_DIR/scripts/make.sh" check` once per session before this pipeline's
CREATE/REFORMAT. It verifies an actual Chromium launch. A named manuscript using
another authoring route follows that route's setup and validation instead;
DOCX-to-PDF does not require Chromium unless it also invokes this pipeline.

When permitted, use `bash "$SKILL_DIR/scripts/make.sh" fix` in an activated Python
virtual environment. On Linux, Chromium may also need
`npx playwright install-deps chromium`. FILL and read-only inspection need Python
and `pypdf`, not the browser pipeline; do not make them install Chromium.

| Tool | Used by | Installation when needed and allowed |
|---|---|---|
| Python 3.9+ | Python scripts | System/runtime |
| `reportlab` | `render_body.py` | `pip install reportlab` |
| `pypdf` | Fill, merge, reformat | `pip install pypdf` |
| Node.js 18+ | `render_cover.js` | System/runtime |
| `playwright` + Chromium | `render_cover.js` | `npm install -g playwright && npx playwright install chromium` |
| `matplotlib` | Math, charts, flowcharts | `pip install matplotlib` |

`make.sh demo` creates sample material, not a finished user deliverable. The
existing `run`, `reformat`, `fill`, `check`, `fix` and `demo` entry points retain
their installed meanings; inspect `make.sh` or relevant script help for uncertain
flags. No manuscript/APA/IEEE/OCR engine modes are added by these guides.
