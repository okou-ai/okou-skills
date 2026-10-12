# okou-skills

A collection of reusable [Agent Skills](https://agentskills.io) that are
independent of the VM0 connector catalog.

Skills follow the [Agent Skills specification](https://agentskills.io/specification).

Skills owned by a VM0 connector live with the connector definition in
[okou-connectors](https://github.com/okou-ai/okou-connectors).

## Principles

1. **Single Ownership**: Keep connector-owned skills in `okou-connectors` and independent skills here
2. **Focused Instructions**: Give agents practical guidance for one well-defined capability
3. **Self-Contained**: Keep each skill's instructions and supporting resources together
4. **Security First**: Document commands in `SKILL.md` for security auditing and compliance checks

## Installation

There are multiple ways to install and use these skills:

### 1. Using Claude Code Marketplace

```bash
# Add marketplace
/plugin marketplace add okou-ai/okou-skills

# Install specific skills
/plugin install github-copilot@vm0-skills
/plugin install hackernews@vm0-skills
```

### 2. Direct Download

```bash
# Clone the repository
git clone https://github.com/okou-ai/okou-skills.git

# Copy to personal skills directory
cp -a okou-skills/github-copilot ~/.claude/skills/
cp -a okou-skills/hackernews ~/.claude/skills/

# Or copy to project directory
cp -a okou-skills/github-copilot ./.claude/skills/
cp -a okou-skills/hackernews ./.claude/skills/
```

After installation, restart Claude Code, then ask "What skills are available?" to see installed skills.

## Contributing

To add a new skill or improve an existing one:

1. If the skill belongs to a VM0 connector, contribute it under
   `connectors/<connector-ref>/skill/` in
   [okou-connectors](https://github.com/okou-ai/okou-connectors).
2. For an independent skill, follow the
   [Agent Skills specification](https://agentskills.io/specification).
3. Include a `SKILL.md` file with tested usage examples.
4. Submit a pull request.

## Analysis and report skills

| Skill | Responsibility |
| --- | --- |
| [analysis-methods](analysis-methods/SKILL.md) | Choose methods from the question and evidence, perform analysis, and support conclusions. Works independently for chat answers and report content. |
| [business-skill-index](business-skill-index/SKILL.md) | Find scenario-specific document structures, templates, and checks in pinned external references. |
| [gen](gen/SKILL.md) | Use Okou artifact-generation commands and their available providers. |
| [office-files](office-files/SKILL.md) | Author, edit, check, and deliver Word, Excel, and PDF files. |

Use only the capabilities the task needs. Analysis does not require artifact
generation, and an existing report can be reformatted without repeating its
analysis. `gen` and `office-files` can use `analysis-methods` when installed;
they do not bundle it or install it implicitly.

The `data-analysis` marketplace bundle includes `analysis-methods` alongside
the existing SQL, statistics, profiling, and quality-check skills. The directory
can also be installed on its own using the direct-download method above.
Registering a skill here does not change Okou's application-managed default
skill list.

## Business document reference index

[business-skill-index](business-skill-index/SKILL.md) provides a
[domain and scenario directory](business-skill-index/references/skill-index.md)
covering 62 skills across 18 scenarios. Agents open one scenario shortlist, then
one skill's metadata file and its pinned source. Supporting templates are read
only when needed. The repository keeps the index and selection prompt, not
copies of the upstream skill collection.

```bash
/plugin install business-skill-index@vm0-skills
```

## Resources

- [Agent Skills Specification](https://agentskills.io/specification)
