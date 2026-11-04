"""Package/documentation contracts, not LLM routing or output-quality tests.

These work from a packaged Office directory without historical Git objects,
installed Office applications, a browser, or optional authoring libraries.
"""
from collections import Counter
import json
from pathlib import Path
import re
import tempfile
import unittest
from urllib.parse import unquote, urlsplit


OFFICE = Path(__file__).resolve().parents[1]
REPO = OFFICE.parent
FORMATS = ("docx", "pdf", "xlsx")
CATEGORIES = {"common", "domains", "operations", "implementation"}


def prose(text):
    """Exclude fenced examples from navigation checks, not from content tests."""
    output, fence = [], None
    for line in text.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if marker:
            token, trailing = marker[1], marker[2]
            if fence is None:
                fence = (token[0], len(token))
            elif (fence[0] == token[0] and len(token) >= fence[1]
                  and not trailing.strip()):
                fence = None
            continue
        if fence is None:
            output.append(line)
    return "\n".join(output)


def targets(text):
    return re.findall(r"\[[^\]\n]+\]\(([^\s)]+)\)", prose(text))


def heading_ids(text):
    counts, result = Counter(), set()
    for heading in re.findall(r"^#{1,6} (.+)$", prose(text), re.M):
        slug = re.sub(r"[^\w -]", "", heading.lower()).replace(" ", "-")
        suffix = f"-{counts[slug]}" if counts[slug] else ""
        counts[slug] += 1
        result.add(slug + suffix)
    return result


def broken_links(paths):
    errors = []
    for origin in paths:
        for target in targets(origin.read_text(encoding="utf-8")):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue
            destination = ((origin.parent / unquote(parsed.path)).resolve()
                           if parsed.path else origin)
            if not destination.is_file():
                errors.append((str(origin), target, "missing file"))
            elif parsed.fragment and destination.suffix == ".md":
                if unquote(parsed.fragment) not in heading_ids(destination.read_text(encoding="utf-8")):
                    errors.append((str(origin), target, "missing heading"))
    return errors


class OfficeDocumentationTests(unittest.TestCase):
    def test_one_office_package_and_three_format_entries(self):
        entries = {p.relative_to(OFFICE).as_posix() for p in OFFICE.rglob("SKILL.md")}
        self.assertEqual(entries, {"SKILL.md", *(f"{kind}/SKILL.md" for kind in FORMATS)})
        for name in entries:
            text = (OFFICE / name).read_text()
            self.assertTrue(text.startswith("---\n"), name)
            self.assertLess(len(text.splitlines()), 500, name)
        root = (OFFICE / "SKILL.md").read_text()
        for kind in FORMATS:
            self.assertIn(f"{kind}/SKILL.md", targets(root))

    def test_every_reference_is_directly_discoverable_from_its_format(self):
        for kind in FORMATS:
            directory = OFFICE / kind
            direct = {urlsplit(t).path for t in targets((directory / "SKILL.md").read_text())}
            for reference in (directory / "references").rglob("*.md"):
                with self.subTest(format=kind, reference=reference.name):
                    self.assertIn(reference.relative_to(directory).as_posix(), direct)

    def test_all_office_markdown_file_and_heading_links_resolve(self):
        self.assertEqual(broken_links(sorted(OFFICE.rglob("*.md"))), [])

    def test_link_checker_detects_broken_file_and_heading_and_ignores_examples(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "target.md").write_text("# One\n\n## Two\n")
            entry = root / "index.md"
            entry.write_text("[ok](target.md#two)\n[missing](absent.md)\n"
                             "[bad anchor](target.md#absent)\n[web](https://example.com/)\n"
                             "```md\n[example](example-only.md)\n```\n")
            self.assertEqual({(e[1], e[2]) for e in broken_links([entry])},
                             {("absent.md", "missing file"),
                              ("target.md#absent", "missing heading")})

    def test_reference_categories_and_filenames_are_consistent(self):
        for kind in FORMATS:
            references = OFFICE / kind / "references"
            self.assertEqual({p.name for p in references.iterdir() if p.is_dir()}, CATEGORIES)
            self.assertEqual(list(references.glob("*.md")), [])
            for path in references.rglob("*.md"):
                with self.subTest(path=path):
                    self.assertEqual(len(path.relative_to(references).parts), 2)
                    self.assertRegex(path.name, r"^[a-z0-9]+(?:-[a-z0-9]+)*\.md$")

    def test_long_references_offer_early_section_navigation(self):
        for kind in FORMATS:
            for path in (OFFICE / kind / "references").rglob("*.md"):
                text = path.read_text()
                if len(text.splitlines()) <= 100:
                    continue
                early = "\n".join(text.splitlines()[:90])
                with self.subTest(path=path):
                    self.assertGreaterEqual(sum(t.startswith("#") for t in targets(early)), 2)

    def test_pdf_schema_has_one_owner_and_readme_is_an_overview(self):
        pdf = OFFICE / "pdf"
        owner = pdf / "references/implementation/content.md"
        self.assertIn("## Block contract", owner.read_text())
        for path in pdf.rglob("*.md"):
            if path != owner:
                self.assertNotIn("## content.json schema", path.read_text(), str(path))
                self.assertNotIn("| Block |", path.read_text(), str(path))
        self.assertLess(len((pdf / "README.md").read_text().splitlines()), 50)
        self.assertFalse((pdf / "design").exists())
        self.assertIn("references/common/presentation.md", (pdf / "scripts/make.sh").read_text())

    def test_new_input_contract_is_loaded_without_changing_read_only_scope(self):
        xlsx = OFFICE / "xlsx"
        for relative in ("SKILL.md", "references/operations/create.md",
                         "references/operations/edit.md", "references/operations/validate.md"):
            text = (xlsx / relative).read_text()
            self.assertTrue(any(t.endswith("common/data-and-inputs.md") for t in targets(text)), relative)
        data = " ".join((xlsx / "references/common/data-and-inputs.md").read_text().split())
        for constraint in ("not permission to add validation", "Do not invent business bounds",
                           "not a GUI entry test", "not a fixed universal operation count"):
            self.assertIn(constraint, data)

    def test_package_ci_includes_shared_checks_without_new_format_registrations(self):
        workflow = (REPO / ".github/workflows/validate-skills.yml").read_text()
        self.assertIn('"office/**"', workflow)
        self.assertIn("python3 -m unittest discover -s office/tests -v", workflow)
        marketplace = json.loads((REPO / ".claude-plugin/marketplace.json").read_text())
        def strings(value):
            if isinstance(value, str):
                yield value
            elif isinstance(value, dict):
                for item in value.values():
                    yield from strings(item)
            elif isinstance(value, list):
                for item in value:
                    yield from strings(item)
        # Marketplace is not the platform's runtime-default registry. Preserve
        # its existing registrations; do not invent separate format plugins.
        registrations = set(strings(marketplace))
        for kind in FORMATS:
            self.assertNotIn(f"./office/{kind}", registrations)


if __name__ == "__main__":
    unittest.main()
