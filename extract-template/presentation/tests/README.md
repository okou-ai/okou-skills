# Presentation extraction regression tests

These are synthetic control/negative cases. They do not replace a real uploaded
PPT reconstruction, source-style acceptance or an actual PPTX roundtrip review.

```bash
python3 -m unittest discover -s extract-template/presentation/tests -p 'test_*.py' -v
npm install --prefix /tmp/presentation-qa playwright@1.64.0
/tmp/presentation-qa/node_modules/.bin/playwright install --with-deps chromium
python3 extract-template/presentation/tests/build-fixtures.py /tmp/presentation-fixtures
PLAYWRIGHT_MODULE=/tmp/presentation-qa/node_modules/playwright \
  FIXTURE_DIR=/tmp/presentation-fixtures \
  BROWSER_REPORT=/tmp/presentation-browser-report.json \
  node extract-template/presentation/tests/browser-test.cjs
```

`CHROMIUM_PATH` optionally selects an installed Chromium. The build script creates
54 local layout adaptations in four controlled combinations: sans/light and
serif/dark, each in English and Chinese. Fixture data and skins stay outside the
reusable library and must not be published as user source/style evidence.

The 36 browser controls include 9.99/10px, SVG/zoom, CJK and mixed runs, the old
80%-cutoff reproduction, rerun/edit/reload idempotence, true clipping versus empty
font-ascent/descent, unresolved fitting, fonts/images/backgrounds, source safe
areas/chrome, zero pages, live four-key navigation, and complete visual-review
coverage. Four additional matrix checks inspect all **216 layout adaptations**.
CI runs the same implementation and archives its JSON result.

The final CLI (`tools/qa.mjs`) additionally requires `agent-browser`. Its prepared
copy is tested separately with `okou presentation screenshot`, actual
`okou presentation convert --verify`, and re-rendering the resulting PPTX.
