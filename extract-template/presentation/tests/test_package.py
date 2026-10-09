import json
import re
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / 'library'


class PackageTests(unittest.TestCase):
    def test_complete_local_library(self):
        catalog = json.loads((LIBRARY / 'references/catalog.json').read_text())
        entries = catalog['layouts']
        self.assertEqual(len(entries), 54)
        self.assertEqual(len({entry['id'] for entry in entries}), len(entries))
        actual = {p.stem for p in (LIBRARY / 'layouts/fragments').glob('*.html')}
        self.assertEqual(actual, {entry['id'] for entry in entries})
        for entry in entries:
            file = (LIBRARY / 'references' / entry['file']).resolve()
            self.assertEqual(file.parent, LIBRARY / 'layouts/fragments')
            source = file.read_text()
            tree = ET.fromstring(source)
            self.assertEqual(tree.get('data-layout'), entry['id'])
            self.assertEqual(sorted({n.get('data-text-role') for n in tree.iter() if n.get('data-text-role')}), entry['roles'])
            self.assertEqual(sorted({n.get('data-repeat') for n in tree.iter() if n.get('data-repeat')}), entry['repeatSlots'])
            self.assertEqual(sorted(set(re.findall(r'\{\{([^{}]+)\}\}', source))), entry['slots'])
            self.assertNotRegex(source, r'<script|<style|style=|https?://|font-family|#[0-9a-fA-F]{3,8}\b')

    def test_geometry_is_not_a_skin(self):
        css = (LIBRARY / 'styles/geometry.css').read_text()
        self.assertNotRegex(css, r'font(?:-family|-size|-weight)?\s*:|(?:background|color|box-shadow|border-radius)\s*:|url\(|@import')

    def test_workflow_is_generation_time_and_public_independent(self):
        source = (ROOT / 'SKILL.md').read_text()
        self.assertIn('**generation** selectively adapts', source)
        self.assertIn('Do not adapt all library fragments during upload', source)
        self.assertIn('10px', source)
        self.assertIn('verify-package.mjs', source)
        self.assertNotIn('Template-artifact', source)
        self.assertNotIn('roleBounds', (ROOT / 'scripts/fit-text.js').read_text())

    def test_installer_and_source_coverage(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            (out / 'layouts/source').mkdir(parents=True)
            (out / 'styles').mkdir()
            shell = '<!doctype html><html><body><div class="deck"></div></body></html>'
            (out / 'layouts/_shell.html').write_text(shell)
            (out / 'SKILL.md').write_text('source guidance')
            (out / 'design-system.md').write_text('source style')
            (out / 'layouts/README.md').write_text('source layouts')
            (out / 'styles/template.css').write_text('.source {color: #123456}')
            (out / 'layouts/source/one.html').write_text('<div class="stage"></div>')
            index = {'sourceFilename': 'original.pptx', 'sourceAspectRatio': '16:9', 'pageCount': 2,
                     'layouts': [{'id': 'one', 'file': 'source/one.html', 'sourcePages': [1, 2],
                                  'purpose': 'source', 'regions': ['title', 'body'], 'capacity': 'short'}]}
            (out / 'layouts/source-index.json').write_text(json.dumps(index))
            command = ['node', str(ROOT / 'scripts/install-qa.mjs'), '--package', str(out)]
            subprocess.run(command, check=True, capture_output=True)
            first = (out / 'layouts/_shell.html').read_text()
            subprocess.run(command, check=True, capture_output=True)
            self.assertEqual(first, (out / 'layouts/_shell.html').read_text())
            self.assertEqual(first.count('BEGIN PRESENTATION RUNTIME'), 1)
            self.assertEqual((out / 'styles/template.css').read_text(), '.source {color: #123456}')
            self.assertEqual((out / 'layouts/source/one.html').read_text(), '<div class="stage"></div>')
            self.assertEqual(len(list((out / 'library/layouts/fragments').glob('*.html'))), 54)
            self.assertEqual(json.loads((out / 'tools/qa-config.json').read_text())['minFontSizePx'], 10)
            self.assertTrue((out / 'references/qa.md').is_file())
            verify = ['node', str(out / 'tools/verify-package.mjs'), '--package', str(out)]
            self.assertEqual(subprocess.run(verify, capture_output=True).returncode, 0)
            index['layouts'][0]['sourcePages'] = [1]
            (out / 'layouts/source-index.json').write_text(json.dumps(index))
            self.assertNotEqual(subprocess.run(verify, capture_output=True).returncode, 0)
            index['layouts'][0]['sourcePages'] = [1, 2]
            index['layouts'][0]['file'] = '../../outside.html'
            (out / 'layouts/source-index.json').write_text(json.dumps(index))
            self.assertNotEqual(subprocess.run(verify, capture_output=True).returncode, 0)

    def test_runtime_is_fixed_at_ten(self):
        metrics = (ROOT / 'scripts/dom-metrics.js').read_text()
        self.assertIn('MIN_FONT_SIZE_PX = 10', metrics)
        fit = (ROOT / 'scripts/fit-text.js').read_text()
        self.assertNotIn('TINY_FLOOR = 11', fit)
        self.assertNotIn('[0.95, 0.9, 0.85, 0.8]', fit)
        self.assertIn('data-presentation-baseline', fit)
        audit = (ROOT / 'tools/audit.js').read_text()
        for key in ('smallText', 'textOverflow', 'keyboardNavigation', 'brokenImage', 'unresolvedFit', 'pageCount'):
            self.assertIn(key, audit)


if __name__ == '__main__':
    unittest.main()
