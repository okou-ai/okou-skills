"""Static DOCX routing/source contracts, not model execution or output-quality tests."""
from pathlib import Path
import re
import subprocess
import unittest
from urllib.parse import unquote, urlsplit


SKILL = Path(__file__).resolve().parents[1]
ROOT = SKILL.parents[1]
CORE = SKILL / "scripts/dotnet/Docx.Core"
ENTRY = SKILL / "SKILL.md"
DOMAINS = SKILL / "references/domains"
AUTHORING = SKILL / "references/implementation/authoring.md"
OWNED_DOCS = [ENTRY, AUTHORING, SKILL / "references/operations/create.md",
              SKILL / "references/operations/template.md",
              SKILL / "references/operations/validate.md", *sorted(DOMAINS.glob("*.md"))]


def read(path):
    return path.read_text(encoding="utf-8")


def links(text):
    return re.findall(r"\[[^\]\n]+\]\(([^)\s]+)\)", text)


def flat(text):
    return " ".join(text.split())


# Prompts are review fixtures. Assertions below check the written routing contract;
# these are not evidence that an LLM chose/read the route or generated a document.
MODEL_CASES = [
    ("government", "Create an editable Chinese 公文 DOCX, GB/T 9704, supplied notice text; no seal or issuing number.",
     "government.md", "A", ["CreateChineseGovernmentDocument", "all-black", "disclosure"]),
    ("apa-professional", "Format supplied study text and references as APA 7 professional DOCX; no new research.",
     "academic.md", "A", ["CreateAPA7Document", "running head", "unindented abstract", "student"]),
    ("chinese-thesis-template", "Put my Chinese thesis in this supplied university DOCX template; preserve cover/TOC and headers.",
     "thesis-template.md", "C-2", ["C-2 Base-Replace", "1/2/3/a", "w:eastAsia", "SDT"]),
    ("hbr-brief", "Create an HBR-style DOCX brief from my supplied text and table.",
     "business-editorial.md", "A", ["CreateHBRStyleDocument", "11 pt Georgia", "Exhibit", "analysis-derived"]),
    ("academic-narrow-edit", "In my APA paper DOCX replace only this date; retain all formatting.",
     None, "B", ["narrow EDIT", "never recreate or restyle", "preserve existing presentation"]),
    ("generic-memo-control", "Create an editable DOCX memo with these To/From/Subject fields, no named style.",
     None, "A", ["Generic memo", "No domain recipe required"]),
]


class DocxDocumentationContracts(unittest.TestCase):
    def test_creator_frontmatter_discovery_and_size(self):
        text = read(ENTRY)
        front = re.match(r"---\n(.*?)\n---", text, re.S).group(1)
        keys = set(re.findall(r"^([a-z][a-z-]*):", front, re.M))
        self.assertLessEqual(keys, {"name", "description", "license", "allowed-tools", "metadata"})
        self.assertNotIn("triggers:", front)
        desc = flat(front.split("description: >\n", 1)[1])
        self.assertLessEqual(len(desc), 1024)
        for trigger in ("Word", "docx", "文档", "Word文档", "报告", "合同", "公文", "排版", "套模板",
                        "GB/T 9704", "IEEE", "ACM", "APA 7 professional", "MLA 9", "Chicago/Turabian",
                        "Springer LNCS", "Nature", "theses", "university templates", "HBR", "Executive Brief"):
            self.assertIn(trigger, desc)
        self.assertIn("not government-policy, research, or legal expertise or official certification", desc)
        self.assertLess(len(text.splitlines()), 500)

    def test_profiles_direct_conditional_and_before_operation(self):
        text = read(ENTRY)
        targets = links(text)
        self.assertEqual({p.name for p in DOMAINS.glob("*.md")},
                         {"government.md", "academic.md", "thesis-template.md", "business-editorial.md"})
        for path in DOMAINS.glob("*.md"):
            self.assertIn(path.relative_to(SKILL).as_posix(), targets)
        for target in ("references/common/cjk-typography.md", "references/implementation/university-template.md",
                       "references/implementation/validation.md"):
            self.assertIn(target, targets)
        self.assertLess(text.index("## Routing order"), text.index("## Pipeline routing"))
        self.assertIn("Condition (within the authorized scope)", text)

    def test_every_owned_markdown_target_and_advertised_resource_exists(self):
        for path in OWNED_DOCS:
            text = read(path)
            for target in links(text):
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                with self.subTest(path=path, target=target):
                    self.assertTrue((path.parent / unquote(parsed.path)).is_file())
            # Existing sample/reference tables use code spans rather than links.
            for target in re.findall(r"`((?:references|assets|scripts|Samples)/[^`\s]+\.(?:md|xml|cs|sh|ps1|xsd))`", text):
                resolved = (CORE / target) if target.startswith("Samples/") else (SKILL / target)
                with self.subTest(path=path, target=target):
                    if "*" in resolved.name:
                        self.assertTrue(any(resolved.parent.glob(resolved.name)), str(resolved))
                    else:
                        self.assertTrue(resolved.is_file(), str(resolved))

    def test_all_thirteen_recipe_symbols_resolve_to_their_linked_source(self):
        source_files = sorted((CORE / "Samples").glob("AestheticRecipeSamples*.cs"))
        self.assertEqual(len(source_files), 5)
        actual = {method: path for path in source_files
                  for method in re.findall(r"public static void (Create\w+)\(string outputPath\)", read(path))}
        self.assertEqual(len(actual), 13)
        advertised = set()
        for profile in DOMAINS.glob("*.md"):
            text = read(profile)
            methods = set(re.findall(r"`(Create[A-Z]\w+)`", text))
            source_links = {(profile.parent / urlsplit(t).path).resolve()
                            for t in links(text) if urlsplit(t).path.endswith(".cs")}
            for method in methods:
                with self.subTest(profile=profile, method=method):
                    self.assertIn(method, actual)
                    self.assertIn(actual[method].resolve(), source_links)
                    self.assertIn("public static partial class AestheticRecipeSamples", read(actual[method]))
            for row in text.splitlines():
                if not row.startswith("|"):
                    continue
                row_sources = {(profile.parent / urlsplit(t).path).resolve()
                               for t in links(row) if urlsplit(t).path.endswith(".cs")}
                for method in re.findall(r"`(Create[A-Z]\w+)`", row):
                    with self.subTest(profile=profile, table_method=method):
                        self.assertIn(actual[method].resolve(), row_sources)
            advertised.update(methods)
        self.assertEqual(advertised, set(actual))
        self.assertIn("references/implementation/authoring.md", links(read(ENTRY)))
        sample_index = read(AUTHORING)
        for path in source_files:
            self.assertIn("Samples/" + path.name, sample_index)

    def test_model_case_written_contracts(self):
        entry = flat(read(ENTRY))
        for name, prompt, profile, operation, tokens in MODEL_CASES:
            with self.subTest(case=name, prompt=prompt):
                contract = flat(read(DOMAINS / profile)) if profile else entry
                for token in tokens:
                    self.assertIn(token, contract)
                if profile:
                    self.assertIn("references/domains/" + profile, entry)
                self.assertIn("Pipeline " + ("C" if operation == "C-2" else operation), entry)
        self.assertEqual(len(MODEL_CASES), 6)

    def test_scope_precedence_and_selective_template_cleanup(self):
        entry = flat(read(ENTRY))
        self.assertIn("explicit user requirements and the supplied template as authoritative", entry)
        self.assertIn("If they conflict, clarify", entry)
        self.assertIn("Named-format rules override generic academic/business defaults", entry)
        self.assertIn("not the user's requirements or template", entry)
        self.assertIn("new creation or explicitly requested restyling", entry)
        self.assertIn("a simple fill remains B", entry)
        self.assertNotIn("Always strip direct formatting", entry)
        self.assertIn("references/implementation/authoring.md", links(read(ENTRY)))
        authoring = flat(read(AUTHORING))
        for token in ("necessary `w:eastAsia`", "semantic emphasis", "numbering", "fields", "relationships",
                      "intentional section structure", "selective cleanup"):
            self.assertIn(token, authoring)
        self.assertIn("**KEEP in `<w:rPr>`:**", read(SKILL / "references/operations/template.md"))

    def test_authoring_referrals_use_real_sections_and_disclose_procedure_limits(self):
        text = read(AUTHORING)
        direct = set(links(text))
        for target in ("../operations/template.md#workflow",
                       "../operations/template.md#template-structure-analysis-required",
                       "../operations/template.md#relationship-id-remapping",
                       "../operations/template.md#3-section-property-conflicts"):
            self.assertIn(target, direct)
        contract = flat(text)
        self.assertIn("not a bundled end-to-end multi-template merge procedure", contract)
        self.assertIn("No dedicated automatic header/footer-transfer procedure or all-section template gate", contract)
        self.assertIn("compare each section and its linked header/footer parts", contract)
        self.assertNotIn("Multi-Template Merge section", text)
        self.assertNotIn("Multi-Section Header/Footer Transfer guidance", text)

    def test_government_and_hbr_source_conflicts_are_scoped(self):
        government = flat(read(DOMAINS / "government.md"))
        for token in ("actual supplied formal letterhead", "do not invent an official seal, issuance number",
                      "all-black simulation", "explicit disclosure", "not an officially certified document"):
            self.assertIn(token, government)
        self.assertIn("All black text, no decorative elements", read(CORE / "Samples/AestheticRecipeSamples.cs"))
        hbr = flat(read(DOMAINS / "business-editorial.md"))
        self.assertIn("not an official HBR template", hbr)
        self.assertIn("Analysis of Harvard Business Review published article formatting",
                      read(CORE / "Samples/AestheticRecipeSamples_Batch4.cs"))
        self.assertNotIn("each with exact values from official style guides", read(ENTRY))

    def test_create_cli_is_generic_and_named_recipes_require_adaptation(self):
        source = read(CORE / "Commands/CreateCommand.cs")
        for name in ("report", "letter", "memo", "academic"):
            self.assertIn(name, source)
        self.assertIn('"academic" => FontDefaults.Academic', source)
        self.assertIn('pageSizeOption.DefaultValueFactory = _ => "letter"', source)
        self.assertNotIn("AestheticRecipeSamples", source)
        self.assertNotIn("academic_styles.xml", source)
        a = flat(read(SKILL / "references/operations/create.md"))
        for token in ("CLI does **not** load these assets", "not APA/IEEE selection", "no named-format CLI flag",
                      "--page-size a4", "not** exact CLI/asset specifications", "CLI's `--type memo` alone"):
            self.assertIn(token, a)
        academic = flat(read(DOMAINS / "academic.md"))
        self.assertIn("Do not deliver their sample content or call them as content-fill APIs", academic)
        self.assertIn("sample content", flat(read(DOMAINS / "thesis-template.md")))
        self.assertIn("never copy sample findings", flat(read(ENTRY)))

    def test_docx_sh_example_flags_exist_in_commands(self):
        command_sources = "\n".join(read(p) for p in (CORE / "Commands").glob("*.cs"))
        # System.CommandLine supplies --help rather than declaring it per command.
        self.assertIn("using System.CommandLine;", command_sources)
        actual_flags = set(re.findall(r'"(--[a-z][a-z-]+)"', command_sources)) | {"--help"}
        for path in OWNED_DOCS:
            text = read(path).replace("\\\n", " ")
            for command in re.findall(r'(?:bash )?"?\$SKILL_DIR/scripts/docx\.sh"?[^`\n]*', text):
                for flag in re.findall(r"--[a-z][a-z-]+", command):
                    with self.subTest(path=path, command=command, flag=flag):
                        self.assertIn(flag, actual_flags)

    def test_validate_contract_matches_command_and_gate_implementation(self):
        source = read(CORE / "Commands/ValidateCommand.cs")
        for token in ('new Option<string>("--gate-check")', 'Template DOCX for gate-check validation',
                      'new PackageValidator().Validate(input)', 'if (xsd != null)', 'if (business)',
                      'gateValidator.Validate(input, gateCheck)'):
            self.assertIn(token, source)
        c = flat(read(SKILL / "references/operations/template.md"))
        for token in ("--gate-check template.docx", "template DOCX", "not an XSD", "not full OOXML validation",
                      "not domain certification", "last section", "explicit ASCII font", "Every template style ID"):
            self.assertIn(token, c)
        self.assertNotIn("--xsd business-rules.xsd", c)
        gate = read(CORE / "Validation/GateCheckValidator.cs")
        for token in ('LastOrDefault()', 'Attribute(W + "ascii")', 'foreach (var style in templateStyles)',
                      'StartsWith("Heading", StringComparison.OrdinalIgnoreCase)'):
            self.assertIn(token, gate)
        guide = read(SKILL / "references/implementation/validation.md")
        self.assertIn("not executable replacements", guide)
        self.assertIn("curated subset", guide)

    def test_source_publication_payload_includes_each_profile_and_source(self):
        # Static source/package inclusion check only; no remote publication is performed.
        workflow = read(ROOT / ".github/workflows/validate-skills.yml")
        self.assertIn("python3 -m unittest discover -s office/docx/tests -v", workflow)
        self.assertIn('"office/**"', workflow)
        payload = set(OWNED_DOCS)
        for path in OWNED_DOCS:
            for target in links(read(path)):
                parsed = urlsplit(target)
                if not parsed.scheme and not parsed.netloc and parsed.path:
                    payload.add((path.parent / unquote(parsed.path)).resolve())
        for path in payload:
            relative = path.relative_to(ROOT).as_posix()
            ignored = subprocess.run(["git", "check-ignore", "--quiet", relative], cwd=ROOT, check=False)
            self.assertEqual(ignored.returncode, 1, relative)
        for name in ("LICENSE", "UPSTREAM.md"):
            self.assertTrue((SKILL / name).is_file())
        # Baseline-preservation is checked once by the implementation run, not
        # hardcoded here: CI may use a shallow clone without historical commits.


if __name__ == "__main__":
    unittest.main()
