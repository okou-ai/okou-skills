# vm0-skills

A collection of reusable [Agent Skills](https://agentskills.io) that are
independent of the VM0 connector catalog.

Skills follow the [Agent Skills specification](https://agentskills.io/specification).

Skills owned by a VM0 connector live with the connector definition in
[vm0-connectors](https://github.com/vm0-ai/vm0-connectors).

## Principles

1. **Single Ownership**: Keep connector-owned skills in `vm0-connectors` and independent skills here
2. **Focused Instructions**: Give agents practical guidance for one well-defined capability
3. **Self-Contained**: Keep each skill's instructions and supporting resources together
4. **Security First**: Document commands in `SKILL.md` for security auditing and compliance checks

## Installation

There are multiple ways to install and use these skills:

### 1. Using Claude Code Marketplace

```bash
# Add marketplace
/plugin marketplace add vm0-ai/vm0-skills

# Install specific skills
/plugin install github-copilot@vm0-skills
/plugin install hackernews@vm0-skills
```

### 2. Direct Download

```bash
# Clone the repository
git clone https://github.com/vm0-ai/vm0-skills.git

# Copy to personal skills directory
cp -a vm0-skills/github-copilot ~/.claude/skills/
cp -a vm0-skills/hackernews ~/.claude/skills/

# Or copy to project directory
cp -a vm0-skills/github-copilot ./.claude/skills/
cp -a vm0-skills/hackernews ./.claude/skills/
```

After installation, restart Claude Code, then ask "What skills are available?" to see installed skills.

## Contributing

To add a new skill or improve an existing one:

1. If the skill belongs to a VM0 connector, contribute it under
   `connectors/<connector-ref>/skill/` in
   [vm0-connectors](https://github.com/vm0-ai/vm0-connectors).
2. For an independent skill, follow the
   [Agent Skills specification](https://agentskills.io/specification).
3. Include a `SKILL.md` file with tested usage examples.
4. Submit a pull request.

## Resources

- [Agent Skills Specification](https://agentskills.io/specification)
