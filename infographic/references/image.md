# Illustration-led image generation

Use this route for a finished raster infographic. Reuse Okou's image backend; these layout/style names describe bundled prompt directions, not CLI flags or registered style IDs.

## Choose a layout

| Message | Layout direction | Composition instructions |
| --- | --- | --- |
| Process | Linear progression | Number the supplied stages once; connect adjacent stages in one reading direction; one explanatory object per stage |
| Comparison | Binary comparison / matrix | Align the same criteria across alternatives; balance visual weight; attach each value to its own item |
| Timeline | Linear progression | Preserve exact chronology; label dates explicitly; do not imply proportional time spacing unless it is correct |
| Hierarchy | Tree branching / layered levels | Draw containment or parent–child branches; never turn a taxonomy into a process |
| Relationship | Hub and spoke | Put the main concept at the center; label the actual relationships; use arrowheads only for stated direction |
| List | Bento / editorial modules | Give each independent takeaway a distinct region; keep one dominant topic illustration, not six competing heroes |

Use a landscape canvas for short sequences and comparisons, portrait for phone-first reading, and square for a compact overview unless the user specified otherwise. Model size support is not guaranteed: inspect the current CLI help and check the actual returned dimensions.

## Choose one style

- **Craft handmade:** cream paper, warm pastel accents, slightly imperfect ink contours or layered cut-paper shapes, ample whitespace, clear illustrated objects. Keep all imagery illustrated; do not mix photorealistic equipment with cartoon figures.
- **Flat editorial:** clean sans-serif labels, geometric vector objects, a restrained set of vibrant fills, one large subject illustration and smaller explanatory details. Avoid floating shapes that communicate nothing.
- **Technical schematic:** deep blue or light drafting paper, consistent fine lines, teal/amber callouts, disciplined geometry. Draw only real components and connections; a blueprint aesthetic does not authorize invented dimensions or engineering claims.

Match the user's brand or supplied references before these defaults. For a named style already present in the live Okou registry, use its compilation packet rather than pretending one of the directions above is a registered ID.

## Compile the prompt

Read [the prompt template](../templates/image-prompt.md), fill every bracketed slot, and save the complete result as `prompt-01.md` in the task folder. Include:

1. One audience and one learning goal.
2. Exact title, subtitle if useful, section labels, body copy, values, and source caption from `copy.json`.
3. A concrete composition: positions, reading direction, relationships, and a topic-specific illustration for each necessary idea.
4. One style and palette; readable Chinese glyphs when applicable.
5. A clear exclusion list: no invented text, extra stages, fabricated values, duplicated numbering, or decorative pseudo-data.

Specify recognizable and physically coherent objects. For example, depict one consistent brewing method rather than combining espresso and pour-over components. Do not add detailed equipment merely to make a scene look richer.

## Submit and retrieve

Inspect the live interface before execution:

```bash
okou generate image -h
```

Pass the complete saved prompt as one safely quoted argument, not just its filename:

```bash
okou generate image --provider built-in --raw-prompt "<complete final prompt>" --wait --json
```

For long or quote-sensitive text, invoke the CLI through an argument array; do not build a shell command by concatenating user content. For example, run this with the task folder as the working directory:

```python
from pathlib import Path
import subprocess

prompt = Path("prompt-01.md").read_text(encoding="utf-8")
with Path("generation-01.json").open("w", encoding="utf-8") as receipt:
    result = subprocess.run(
        ["okou", "generate", "image", "--provider", "built-in",
         "--raw-prompt", prompt, "--wait", "--json"],
        stdout=receipt, text=True, check=False,
    )
# Inspect the receipt and exit status. Do not automatically resubmit on failure.
```

Add supported size/quality/reference-image flags only when the actual request calls for them. Do not pass `--model`; built-in generation follows Settings. If using a reference, pass it through the supported reference-image flag instead of claiming the model saw a file it never received.

Save the durable generation ID. If the wait ends without a completed artifact, use the same job:

```bash
okou generate get <generation-id> --json
okou generate get <generation-id> --refresh --json
okou generate get <generation-id> --out /absolute/task/infographic.png
```

These are independent retrieval/progress operations, not instructions to poll forever or submit another job. Read the actual status, receipt and errors before choosing the next action. For credit/auth failures, follow the platform's current diagnostics.

## Review and correct

Download when needed and open the actual final image. Read every string against `copy.json`; inspect object structure, arrows, labels, and stage count. Record requested versus actual dimensions and the returned model, never assumed values.

After a confirmed defect, write `prompt-02.md` describing the precise correction while retaining all required copy. Make at most one additional paid generation within the user's budget. A timed-out or unknown job is not a confirmed failure and does not justify a replacement request. If the second candidate is still wrong, stop and report the defect or ask whether to continue spending.

Do not replace bitmap text with code, silently switch to HTML/SVG, or call the resulting PNG editable. Follow the main skill's upload and delivery instructions.
