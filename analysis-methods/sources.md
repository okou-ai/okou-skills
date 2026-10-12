# Sources and adaptation

This package selectively adapts MIT-licensed analytical instructions from the
following fixed upstream revisions. It is maintained in Okou; runtime use does
not download or execute those upstream repositories.

| Upstream | Pinned revision | Retained material |
| --- | --- | --- |
| [DeerFlow](https://github.com/bytedance/deer-flow/tree/1f15e0b43ca58b9601514f9f5c408fb032022833) | `1f15e0b43ca58b9601514f9f5c408fb032022833` | Question/domain routing, complementary and data-feasible framework selection, per-question data requirements, schema-first analysis and evidence-backed reports |
| [Scientific Agent Skills](https://github.com/K-Dense-AI/scientific-agent-skills/tree/92ace75ac21efe19a620434e0ca4e356081fe807) | `92ace75ac21efe19a620434e0ca4e356081fe807` | Market definitions, claim/source separation, reproducible calculations, statistical design and assumptions, uncertainty, rival hypotheses and critical appraisal |

## Upstream files inspected and adapted

- DeerFlow: [`consulting-analysis/SKILL.md`](https://github.com/bytedance/deer-flow/blob/1f15e0b43ca58b9601514f9f5c408fb032022833/skills/public/consulting-analysis/SKILL.md)
  and [`data-analysis/SKILL.md`](https://github.com/bytedance/deer-flow/blob/1f15e0b43ca58b9601514f9f5c408fb032022833/skills/public/data-analysis/SKILL.md).
- Scientific Agent Skills:
  [`market-research-reports/SKILL.md`](https://github.com/K-Dense-AI/scientific-agent-skills/blob/92ace75ac21efe19a620434e0ca4e356081fe807/skills/market-research-reports/SKILL.md),
  [`statistical-analysis/SKILL.md`](https://github.com/K-Dense-AI/scientific-agent-skills/blob/92ace75ac21efe19a620434e0ca4e356081fe807/skills/statistical-analysis/SKILL.md),
  [`scientific-critical-thinking/SKILL.md`](https://github.com/K-Dense-AI/scientific-agent-skills/blob/92ace75ac21efe19a620434e0ca4e356081fe807/skills/scientific-critical-thinking/SKILL.md),
  and [`hypothesis-generation/SKILL.md`](https://github.com/K-Dense-AI/scientific-agent-skills/blob/92ace75ac21efe19a620434e0ca4e356081fe807/skills/hypothesis-generation/SKILL.md).

The local Python helpers and tests are Okou implementations of the documented
CSV profiling and evidence-record contracts, not copied upstream scripts.

## Deliberate scope

Retained: general business research, market/competitive questions, data analysis,
method selection, evidence checking and reports in the user's chosen format.

Excluded: scientific/clinical/laboratory workflows, specialty databases, trading
execution, provider/model bindings, product promotion, paid diagram generation,
upstream runtime paths and dependency installers, mandatory word/page/framework
quotas, and consulting-brand voice imitation. Rendering uses Okou's existing
skills and selected templates; this package supplies analytical content guidance.

Adaptations keep input checks and uncertainty proportional to the question.
They are not validation of every upstream method or a claim of equivalent output
quality. Updating a source requires reviewing the affected guidance and rerunning
the helper and behavioral checks.

## Licenses

Keep both copyright and MIT permission notices with this package:

- [DeerFlow MIT notice](licenses/deerflow-MIT.txt)
- [K-Dense MIT notice](licenses/scientific-skills-MIT.txt)
