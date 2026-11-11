import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const read = (name) => fs.readFileSync(path.join(root, name), 'utf8');

test('entry is a concise operational skill, not an RFC or initializer scaffold', () => {
  const text = read('SKILL.md');
  assert.match(text, /^---\nname: infographic\ndescription: /);
  assert.ok(text.split('\n').length < 150);
  assert.doesNotMatch(text, /TODO|待评审|D0：|Structuring This Skill/);
  assert.match(text, /render\.mjs/);
  assert.match(text, /actual image/);
});

test('all operational reference links resolve inside the complete package', () => {
  for (const name of ['SKILL.md', 'references/antv.md', 'references/image.md', 'UPSTREAM.md']) {
    const text = read(name);
    for (const [, target] of text.matchAll(/\]\(([^)]+)\)/g)) {
      if (/^https?:\/\//.test(target) || target.startsWith('#')) continue;
      const resolved = path.resolve(root, path.dirname(name), target.split('#')[0]);
      assert.ok(resolved.startsWith(root), `${name}: unsafe relative link ${target}`);
      assert.ok(fs.existsSync(resolved), `${name}: missing ${target}`);
    }
  }
});

test('all six native starter layouts are bundled', () => {
  for (const name of ['process', 'comparison', 'timeline', 'hierarchy', 'relation', 'list']) {
    const text = read(`templates/${name}.antv`);
    assert.match(text, /^infographic /);
    assert.match(text, /\ndata\n/);
    assert.doesNotMatch(text, /TODO|<placeholder>/);
  }
});

test('renderer dependencies are exactly pinned and agree with the lockfile', () => {
  const pkg = JSON.parse(read('package.json'));
  const lock = JSON.parse(read('package-lock.json'));
  assert.equal(pkg.private, true);
  assert.equal(pkg.engines.node, '>=22.12.0');
  assert.equal(lock.packages[''].engines.node, pkg.engines.node);
  assert.match(read('references/antv.md'), /Node 22\.12\.0\+/);
  assert.equal(pkg.dependencies['@antv/infographic'], '0.2.20');
  for (const [name, version] of Object.entries(pkg.dependencies)) {
    assert.match(version, /^\d+\.\d+\.\d+$/);
    assert.equal(lock.packages[''].dependencies[name], version);
  }
});

test('image route is usable without another provider key or a fixed model', () => {
  const text = read('references/image.md');
  assert.match(text, /--raw-prompt/);
  assert.match(text, /--wait/);
  assert.match(text, /same job/);
  assert.match(text, /Do not pass `--model`/);
  assert.doesNotMatch(text, /GEMINI_API_KEY|FAL_KEY|OPENAI_API_KEY/);
  assert.match(read('templates/image-prompt.md'), /EXACT VISIBLE COPY/);
});

test('source attribution and upstream license texts are preserved', () => {
  for (const name of ['antv', 'baoyu', 'epic', 'remy']) {
    const text = read(`licenses/${name}-MIT.txt`);
    assert.match(text, /MIT License/);
    assert.match(text, /Copyright/);
    assert.match(text, /Permission is hereby granted/);
  }
  for (const [, sha] of read('UPSTREAM.md').matchAll(/github\.com\/[^\s)]+\/(?:tree|blob)\/([^/)\s]+)/g)) {
    assert.match(sha, /^[0-9a-f]{40}$/);
  }
});

test('repository marketplace entry points to this skill when tested in the repository', (t) => {
  const manifest = path.resolve(root, '../.claude-plugin/marketplace.json');
  if (!fs.existsSync(manifest)) return t.skip('standalone package has no repository marketplace');
  const plugins = JSON.parse(fs.readFileSync(manifest, 'utf8')).plugins;
  const entries = plugins.filter((entry) => entry.name === 'infographic');
  assert.equal(entries.length, 1);
  assert.deepEqual(entries[0].skills, ['./infographic']);
});
