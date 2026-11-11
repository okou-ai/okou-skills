# Prompt framework

> Modified adaptation of SuperCMO photographic guidance and buluslan's structured
> prompt approach. Retain the [source notices](../THIRD_PARTY_NOTICES.md).

## Brief

Gather these as ordinary notes, not a required JSON form:

- **Product:** real reference or delegated fictional concept; observed/defined
  appearance, state, details to preserve, and unknowns.
- **References:** actual images, their order, and each image's permitted role.
- **Purpose and look:** shot type, placement/audience when relevant, and visual direction.
- **Frame:** viewpoint, crop, focus, product region/components and printing that must appear.
- **Set and light:** background, supporting surface, props, key, fill, and shadows.
- **Text and constraints:** existing print to preserve, exact authorized fictional
  label strings if any, must-include and must-avoid elements.
- **Output:** requested size/ratio, format/background, and quality within the user's scope.

## Eight-block scaffold

Replace every placeholder with concrete photographic instructions. Resolve
conflicts and actual attachment order first; never describe an unattached image
as attached. Keep technical flags, private source URLs, and unsupported product
claims outside the prompt. Use the user's requested prompt language, preserving
exact supplied text in its original script and case.

```text
[1. REFERENCE ROLES AND IDENTITY]
{Map actual Image 1, Image 2, etc. to their roles and preservation constraints;
or explicitly identify a fictional product with no identity reference.}

[2. SHOT OBJECTIVE AND PRODUCT STATE]
{Photograph's purpose, evidenced state, and product description. Describe a
fictional product fully; avoid re-specifying details already settled by a real reference.}

[3. COMPOSITION AND CAMERA]
{Supported viewpoint, product position, required visible region, crop and focus.}

[4. SET AND PROPS]
{One coherent setting, support surface, and subordinate approved styling props.}

[5. LIGHT AND MATERIALS]
{Key direction/softness, fill/separation, contact/cast shadows and material response.}

[6. LOOK AND COLOR]
{Physical art direction and colors bound to specific surfaces/objects;
protect a real product's own color.}

[7. TEXT]
{Preserve existing reference printing without redesign; or quote exact newly
authorized fictional label text. Add no unrequested lettering or claims.}

[8. EXCLUSIONS AND FRAMING]
{Concise task-specific exclusions and delivery-crop intent, not a generic blacklist.}
```

Keep prose natural within the blocks; the labels organize instructions, not API
parameters. Agree the visible region and required printing before generation:
an unprinted seam macro may exclude source branding, but a required label cannot
be excused as an intentional crop after a failed output.

## Example: fictional yuzu-soda hero

This example assumes the user delegated a fictional beverage design and the
exact label strings. It is a prompt example, not a generation result.

```text
[1. REFERENCE ROLES AND IDENTITY]
Create a fictional beverage concept, not a photograph of an existing SKU.
There are no attached reference images.

[2. SHOT OBJECTIVE AND PRODUCT STATE]
Photograph one sealed slim aluminium yuzu-soda can as a summer brand hero.
Use a pale butter-yellow body, plain silver lid and pull tab, short dark-green
label, and small plausible condensation droplets. Keep it upright and sealed.

[3. COMPOSITION AND CAMERA]
Use a portrait 2:3 frame and a slightly elevated front view with restrained
perspective. Show the entire can just right of center; keep label and rim sharp,
with only the distant background softer and no blank headline panel.

[4. SET AND PROPS]
Rest the can on pale mint-green ceramic tile with fine joints. Place one cut
yuzu and one whole yuzu low to the left as subordinate styling props.

[5. LIGHT AND MATERIALS]
Use neutral daylight from upper left, moderately directional with slightly soft
shadow edges. Cast the shadow toward lower right, ground the base with a contact
shadow, and show smooth aluminium tonal reflections and clean silver-rim highlights.

[6. LOOK AND COLOR]
Keep the scene fresh and sunlit, with open shadow detail and restrained saturation.
Bind pale yellow to the can, mint green to tile, citrus yellow to fruit, and dark
green to the fictional label.

[7. TEXT]
The only new wording is exactly "YUZU" above "SODA" in legible dark-green
uppercase letters. Add no other words, badges, or nutrition claims.

[8. EXCLUSIONS AND FRAMING]
Make one coherent photographic frame, not a collage or finished ad. Avoid a
duplicated tab, swollen geometry, smeared lettering, floating fruit, inconsistent
shadows, oversized droplets, or props blocking the label.
```

## Example: reference-product fragrance hero

Use only after attaching and inspecting the actual product image. This example
assumes the source confirms a closed fragrance bottle in a front view; adapt it
to the real evidence. It does not establish that any real SKU has been inspected.

```text
[1. REFERENCE ROLES AND IDENTITY]
Image 1 is the product identity reference. Use the same bottle, preserving its
silhouette, proportions, cap, glass color, label placement, and existing printing.
It supplies product identity, not the new background; do not redesign the label.

[2. SHOT OBJECTIVE AND PRODUCT STATE]
Create a low-key brand hero photograph of that fragrance bottle, closed,
upright, and assembled exactly as evidenced in Image 1.

[3. COMPOSITION AND CAMERA]
Use the same front-facing viewpoint in a portrait 2:3 frame, with the whole
bottle visible and centered. Keep cap, label and outline legible; soften the
distant background without distorting glass edges.

[4. SET AND PROPS]
Place the bottle on charcoal stone against a subdued dark background, with no
extra bottles, loose caps, liquid spills, or unrelated props.

[5. LIGHT AND MATERIALS]
Use a broad oblique key from upper left, controlled label fill, and a restrained
edge highlight. Show a soft contact shadow on the stone and material-appropriate
glass/cap reflections, with no unexplained second hard shadow.

[6. LOOK AND COLOR]
Use restrained low-key treatment with readable shadows and tactile stone.
Keep the product's colors and finish faithful to Image 1; darken the environment,
not the SKU.

[7. TEXT]
Preserve only existing product printing from Image 1. Add no new wording,
logos, decorative lettering, claims, or signatures.

[8. EXCLUSIONS AND FRAMING]
Make one photographic frame. Avoid changed cap geometry, doubled edges, warped
printing, crushed label detail, invented rear surfaces, or an ungrounded base.
Keep all required components within the delivery crop.
```
