---
name: deep-dive
description: Staged codebase research and solution design for explicitly requested deep research/deep innovate or an agreed research-before-design engagement. Not a default dependency for ordinary document analysis, general investigation, or a request that already asks for findings and recommendations together.
---

# Staged research and solution design

Use the phases below only when the user selected this staged engagement. Broad
words such as "analyze", "investigate" or "调研" alone do not require phase
files or a facts-only handoff. For ordinary analysis, answer the requested
question in the requested format, including recommendations when asked.
Do not turn a clear, authorized implementation request into another mandatory
research/feedback round.

## Operation: deep research

**Usage:** `deep research [task description]`

Information gathering phase. Analyze the codebase without suggesting solutions.

### Restrictions

**PERMITTED:**
- Reading files and code
- Asking clarifying questions
- Understanding code structure and architecture
- Analyzing dependencies and constraints
- Recording findings

**FORBIDDEN:**
- Suggestions or recommendations
- Implementation ideas
- Planning or roadmaps
- Any hint of action

### Workflow

1. **Clarification** - Ask only questions that block the agreed research scope; reuse resolved context
2. **Research** - Systematically analyze relevant code
3. **Documentation** - Record findings to `deep-dive/{task-name}/research.md`
4. **Completion** - Summarize findings (facts only), ask what to do next

### research.md Structure

```markdown
# Research: {task-name}

## Scope

What was investigated and why.

## Findings

### Architecture
- Current structure and patterns observed

### Dependencies
- Libraries, services, and internal modules involved

### Constraints
- Technical limitations, compatibility requirements

### Data Flow
- How data moves through the relevant components

## Open Questions

- Unresolved items that need clarification
```

## Operation: deep innovate

**Usage:** `deep innovate [task description]`

Creative brainstorming phase. Explore multiple approaches based on research findings.

### Prerequisites

Research document must exist at `deep-dive/{task-name}/research.md`

### Restrictions

**PERMITTED:**
- Discussing multiple solution ideas
- Evaluating advantages and disadvantages
- Exploring architectural alternatives
- Comparing technical strategies
- Considering trade-offs

**FORBIDDEN:**
- Concrete planning with specific steps
- Implementation details or pseudo-code
- Committing to a single solution
- File-by-file change specifications

### Workflow

1. **Review** - Read research document, summarize key findings
2. **Exploration** - Generate 2-3 distinct solution approaches
3. **Analysis** - Document pros/cons, trade-offs for each
4. **Documentation** - Create `deep-dive/{task-name}/innovate.md`
5. **Discussion** - Present approaches, gather user feedback

### innovate.md Structure

For each approach, document:

```markdown
# Innovation: {task-name}

## Research Summary

Key findings from the research phase.

## Approach A: {name}

### Core Concept
Philosophy and high-level idea.

### Advantages
- ...

### Challenges / Risks
- ...

### Compatibility
How it fits with existing architecture.

### Scalability & Maintainability
Long-term considerations.

## Approach B: {name}

(same structure)

## Approach C: {name}

(same structure)

## Comparison Matrix

| Criterion        | Approach A | Approach B | Approach C |
|------------------|------------|------------|------------|
| Complexity       |            |            |            |
| Risk             |            |            |            |
| Time to deliver  |            |            |            |
| Maintainability  |            |            |            |

## Next Steps

Awaiting user decision before proceeding.
```
