#!/usr/bin/env node

import { constants } from 'node:fs';
import { lstat, mkdir, open, readFile, readdir } from 'node:fs/promises';
import { dirname, join, parse, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const defaultLibraryDir = fileURLToPath(new URL('../assets/layout-library/', import.meta.url));

async function statOrMissing(path) {
  try {
    return await lstat(path);
  } catch (error) {
    if (error.code === 'ENOENT') return null;
    throw error;
  }
}

// Check ancestors too: O_NOFOLLOW on the final file alone does not protect a
// package whose layouts/ or styles/ directory points outside the package.
async function inspectPath(path, kind) {
  const absolute = resolve(path);
  const root = parse(absolute).root;
  const parts = absolute.slice(root.length).split(sep).filter(Boolean);
  let current = root;
  for (let index = 0; index < parts.length; index += 1) {
    current = join(current, parts[index]);
    const stat = await statOrMissing(current);
    if (!stat) return null;
    if (stat.isSymbolicLink()) throw new Error(`Refusing symbolic link: ${current}`);
    const final = index === parts.length - 1;
    if (!final || kind === 'directory') {
      if (!stat.isDirectory()) throw new Error(`Expected a directory: ${current}`);
    } else if (!stat.isFile()) {
      throw new Error(`Expected a regular file: ${current}`);
    }
    if (final) return stat;
  }
  return lstat(root);
}

async function readLibraryFile(path) {
  if (!(await inspectPath(path, 'file'))) throw new Error(`Missing library file: ${path}`);
  return readFile(path);
}

/** Copy the shared library without replacing package-owned brand/source files. */
export async function installLayoutLibrary({ packageDir, libraryDir = defaultLibraryDir }) {
  if (!packageDir) throw new Error('A package directory is required.');
  const destination = resolve(packageDir);
  const library = resolve(libraryDir);
  const fragmentsDir = join(library, 'fragments');
  if (!(await inspectPath(fragmentsDir, 'directory'))) {
    throw new Error(`Missing library fragments: ${fragmentsDir}`);
  }
  const fragmentNames = (await readdir(fragmentsDir)).filter((name) => name.endsWith('.html')).sort();
  if (fragmentNames.length < 40) {
    throw new Error(`The shared library must contain at least 40 layouts; found ${fragmentNames.length}.`);
  }

  const entries = [
    ...fragmentNames.map((name) => ({ source: join('fragments', name), target: join('layouts', 'common', name) })),
    { source: 'catalog.json', target: join('layouts', 'common', 'catalog.json') },
    { source: 'layout.css', target: join('styles', 'layout.css') },
    { source: 'theme.css', target: join('styles', 'theme.css'), preserve: true },
    { source: 'shell.html', target: join('layouts', '_shell.html'), preserve: true },
    { source: 'chrome.html', target: join('layouts', 'chrome.html'), preserve: true },
  ];

  // Complete validation before creating even the package directory. A conflict
  // in the last fragment must not leave an incomplete library in the package.
  await inspectPath(destination, 'directory');
  const planned = [];
  const result = { packageDir: destination, layouts: fragmentNames.length, copied: [], unchanged: [], preserved: [] };
  for (const entry of entries) {
    const content = await readLibraryFile(join(library, entry.source));
    const target = join(destination, entry.target);
    const existing = await inspectPath(target, 'file');
    if (!existing) {
      planned.push({ ...entry, target, content });
    } else if (entry.preserve) {
      result.preserved.push(entry.target);
    } else if ((await readFile(target)).equals(content)) {
      result.unchanged.push(entry.target);
    } else {
      throw new Error(`Library file differs: ${target}. Keep the existing package intact and install into a fresh directory to compare versions.`);
    }
  }

  for (const entry of planned) {
    await inspectPath(dirname(entry.target), 'directory');
    await mkdir(dirname(entry.target), { recursive: true });
    await inspectPath(dirname(entry.target), 'directory');
    const file = await open(entry.target, constants.O_WRONLY | constants.O_CREAT | constants.O_EXCL | constants.O_NOFOLLOW, 0o644);
    try {
      await file.writeFile(entry.content);
    } finally {
      await file.close();
    }
    result.copied.push(relative(destination, entry.target));
  }
  return result;
}

const usage = 'Usage: node scripts/install-layout-library.mjs --package <template-directory>';

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  if (args.length === 1 && (args[0] === '--help' || args[0] === '-h')) {
    console.log(usage);
  } else if (args.length !== 2 || args[0] !== '--package' || !args[1] || args[1].startsWith('--')) {
    console.error(usage);
    process.exitCode = 1;
  } else {
    try {
      const result = await installLayoutLibrary({ packageDir: args[1] });
      console.log(JSON.stringify(result, null, 2));
    } catch (error) {
      console.error(`Layout library installation failed: ${error.message}`);
      process.exitCode = 1;
    }
  }
}
