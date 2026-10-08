"""Compile a small, source-bound token set to scoped CSS. Standard library only."""
import argparse
import copy
import json
import math
import re
from pathlib import Path

NAME = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*(?:\.[a-z][a-z0-9]*(?:-[a-z0-9]+)*)+$")
ALIAS = re.compile(r"^\{([^{}]+)\}$")
COLOR = re.compile(r"^#[0-9a-f]{6}(?:[0-9a-f]{2})?$")
ROLE_PARENT = {"title": None, "body": None, "heading": "title", "metric-value": "title", "metric-label": "body", "label": "body", "caption": "body", "table-header": "body", "table-cell": "body"}
TYPE_PROPERTIES = {"font-family": "font-family", "font-size": "dimension", "font-weight": "number", "line-height": "number", "letter-spacing": "dimension", "paragraph-gap": "dimension"}
CORE = ["color.surface.canvas", "color.on-surface.canvas.primary"] + [f"type.{role}.{prop}" for role in ("title", "body") for prop in ("font-family", "font-size")]


def alias_target(value):
    match = ALIAS.fullmatch(value) if isinstance(value, str) else None
    return match.group(1) if match else None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def compile_theme(document, roles=None, profile=None, surface=None):
    require(document.get("contractVersion") == "1.0.0", "Unsupported contractVersion")
    tokens = copy.deepcopy(document.get("$tokens", {}))
    require(isinstance(tokens, dict), "$tokens must be an object")
    scope = ".okp-theme"
    for kind, selected in (("profiles", profile), ("surfaces", surface)):
        if selected is not None:
            require(bool(re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", selected)), "Invalid context ID")
            scope += f'[data-{"type-profile" if kind == "profiles" else "surface"}="{selected}"]'
            context = document.get("contexts", {}).get(kind, {}).get(selected)
            require(context is not None, f"Unknown {kind}: {selected}")
            for name, token in context["$tokens"].items():
                if kind == "surfaces":
                    require(name.startswith(("color.", "chart.", "component.")) and token["$type"] in ("color", "color-list"), "Surface overrides may not change typography or geometry")
            if kind == "surfaces":
                touched = set()
                for name in context["$tokens"]:
                    match = re.fullmatch(r"color\.(?:surface|border)\.([a-z0-9-]+)|color\.on-surface\.([a-z0-9-]+)\.(?:primary|secondary)", name)
                    if match: touched.add(match.group(1) or match.group(2))
                for id_ in touched:
                    require(all(name in context["$tokens"] for name in (f"color.surface.{id_}", f"color.on-surface.{id_}.primary", f"color.on-surface.{id_}.secondary", f"color.border.{id_}")), "SURFACE_OVERRIDE_PAIR_INCOMPLETE: " + id_)
            tokens.update(copy.deepcopy(context["$tokens"]))
    require(all(name in tokens for name in CORE), "Missing core tokens: " + ", ".join(name for name in CORE if name not in tokens))
    selected_roles = list(dict.fromkeys(["title", "body"] + (list(ROLE_PARENT) if roles is None else list(roles))))
    require(all(re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", role) for role in selected_roles), "Invalid text role")
    for role in selected_roles:
        if role not in ROLE_PARENT:
            require(all(f"type.{role}.{prop}" in tokens for prop in ("font-family", "font-size")), "Extension role needs explicit font bindings: " + role)
    inferred = []
    role_map = {}
    for role in selected_roles:
        parent = ROLE_PARENT.get(role)
        role_map[role] = role if f"type.{role}.font-size" in tokens else parent
        if parent:
            for prop, type_ in TYPE_PROPERTIES.items():
                name, fallback = f"type.{role}.{prop}", f"type.{parent}.{prop}"
                if name not in tokens and fallback in tokens:
                    tokens[name] = {"$type": type_, "$value": "{" + fallback + "}", "$extensions": {"origin": {"kind": "inferred", "reason": f"Role not observed; reuse {fallback} without changing its size."}}}
                    inferred.append(name)
    for name, source in (("color.on-surface.canvas.secondary", "color.on-surface.canvas.primary"), ("color.border.canvas", "color.on-surface.canvas.primary")):
        if name not in tokens:
            tokens[name] = {"$type": "color", "$value": "{" + source + "}", "$extensions": {"origin": {"kind": "inferred", "reason": "No separate source role; preserve primary foreground rather than invent a color."}}}
            inferred.append(name)
    resolved, origins, active, css_names = {}, {}, set(), {}

    def resolve(name):
        require(name in tokens, "TOKEN_REF_MISSING: " + name)
        require(name not in active, "TOKEN_REF_CYCLE: " + name)
        if name in resolved:
            return resolved[name]
        token = tokens[name]
        require(NAME.fullmatch(name), "TOKEN_NAME_INVALID: " + name)
        require(name.split(".")[0] in ("ref", "color", "type", "space", "shape", "stroke", "chart", "component"), "TOKEN_LAYER_VIOLATION: " + name)
        css_name = "--okp-" + name.replace(".", "-")
        require(css_name not in css_names or css_names[css_name] == name, "TOKEN_CSS_NAME_COLLISION: " + name)
        css_names[css_name] = name
        active.add(name)
        type_, value = token["$type"], token["$value"]
        target = alias_target(value)
        if target:
            require(not name.startswith("ref."), "Source values may not alias other layers")
            require(target.split(".")[0] not in ("runtime", "fit", "layout"), "TOKEN_LAYER_VIOLATION: " + target)
            require(target in tokens, "TOKEN_REF_MISSING: " + target)
            require(tokens[target]["$type"] == type_, "TOKEN_TYPE_MISMATCH: " + name)
            if name.startswith("component."):
                require(not target.startswith("ref."), "Components must bind through semantic roles")
            else:
                require(not target.startswith("component."), "Semantic roles may not depend on component skins")
            value = resolve(target)
            origin = token.get("$extensions", {}).get("origin", origins[target])
        else:
            origin = token.get("$extensions", {}).get("origin")
            if type_ == "color-list":
                require(isinstance(value, list) and value, "Invalid color-list: " + name)
                colors = []
                for item in value:
                    target = alias_target(item)
                    if target:
                        require(target in tokens and tokens[target]["$type"] == "color", "Invalid palette alias")
                        require(not target.startswith("component."), "Palette cannot depend on a component")
                        item = resolve(target)
                    require(isinstance(item, str) and COLOR.fullmatch(item), "Invalid palette color")
                    colors.append(item)
                value = colors
        require(isinstance(origin, dict) and origin.get("kind") in ("extracted", "inferred", "user", "library"), "TOKEN_ORIGIN_MISSING: " + name)
        if origin["kind"] == "inferred":
            require(bool(origin.get("reason")), "Inference needs a reason: " + name)
        if origin["kind"] == "extracted":
            require(bool(origin.get("documentId")) and bool(origin.get("location")), "Extracted value needs a source location: " + name)
        if type_ == "color":
            require(isinstance(value, str) and COLOR.fullmatch(value), "Invalid color: " + name)
        elif type_ == "dimension":
            require(isinstance(value, dict) and set(value) == {"value", "unit"} and value["unit"] == "px", "Dimensions must be normalized px: " + name)
            require(isinstance(value["value"], (int, float)) and not isinstance(value["value"], bool) and math.isfinite(value["value"]), "Invalid dimension: " + name)
            if not name.startswith("ref.") and not name.endswith(".letter-spacing"):
                require(value["value"] >= 0, "Negative dimension: " + name)
            if name.endswith(".font-size"):
                require(value["value"] > 0, "Non-positive font size: " + name)
        elif type_ == "font-family":
            require(isinstance(value, list) and value and all(isinstance(v, str) and v and not any(c in v for c in "\r\n") for v in value), "Invalid font family: " + name)
        elif type_ == "number":
            require(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value), "Invalid number: " + name)
            if name.endswith(".font-weight"):
                require(float(value).is_integer() and 1 <= value <= 1000, "Invalid font weight")
            if name.endswith(".line-height"):
                require(value > 0, "Invalid line height")
        elif type_ == "string":
            require(isinstance(value, str) and value in ("inherit", "canvas", "panel", "accent", "inverse"), "Unsupported binding enum: " + name)
        elif type_ == "boolean":
            require(isinstance(value, bool), "Invalid boolean: " + name)
        elif type_ != "color-list":
            raise ValueError("Unknown token type: " + type_)
        active.remove(name)
        resolved[name], origins[name] = value, origin
        return value

    for name in tokens:
        resolve(name)
    for role in selected_roles:
        for prop, type_ in TYPE_PROPERTIES.items():
            name = f"type.{role}.{prop}"
            if name in tokens:
                require(tokens[name]["$type"] == type_, "Wrong role property type: " + name)
    for name in CORE[:2]:
        require(tokens[name]["$type"] == "color", "Core color has incorrect type")
    component_types = {"component.card.surface-role": "string", "component.table.header-surface-role": "string", "component.card.border-color": "color", "component.table.rule-color": "color", "component.connector.color": "color"}
    for name in ("component.card.padding", "component.card.border-width", "component.card.radius", "component.table.cell-padding", "component.table.rule-width", "component.connector.stroke-width"):
        component_types[name] = "dimension"
    for edge in ("top", "right", "bottom", "left"):
        component_types["component.card.padding-" + edge] = "dimension"
        component_types["component.table.cell-padding-" + edge] = "dimension"
    for name, type_ in component_types.items():
        if name in tokens: require(tokens[name]["$type"] == type_, "Wrong component property type: " + name)
    for surface_role in ("canvas", "panel", "accent", "inverse"):
        if "color.surface." + surface_role in tokens:
            require(all(name in tokens for name in (f"color.on-surface.{surface_role}.primary", f"color.on-surface.{surface_role}.secondary", f"color.border.{surface_role}")), "SURFACE_PAIR_INCOMPLETE: " + surface_role)
    body_size = resolved["type.body.font-size"]["value"]
    for gap in ("section-gap", "column-gap", "item-gap"):
        name = "space." + gap
        if name not in resolved:
            css_name = "--okp-" + name.replace(".", "-")
            require(css_name not in css_names, "TOKEN_CSS_NAME_COLLISION: " + name)
            resolved[name] = {"value": body_size, "unit": "px"}
            tokens[name] = {"$type": "dimension"}
            origins[name] = {"kind": "inferred", "reason": "Unobserved spacing: use one body em as an explicit pilot mapping; validate against source before publishing."}
            inferred.append(name)
    declarations = []
    generic_fonts = {"serif", "sans-serif", "monospace", "system-ui"}
    for name, value in sorted(resolved.items()):
        type_ = tokens[name]["$type"]
        if type_ in ("color-list", "string", "boolean"):
            continue
        if type_ == "dimension": value = f"{value['value']:g}px"
        elif type_ == "font-family": value = ", ".join(v if v in generic_fonts else json.dumps(v, ensure_ascii=False) for v in value)
        elif type_ == "number": value = f"{value:g}"
        # CSS must remain safe when embedded in a standalone <style> element.
        value = str(value).replace("<", "\\3c ")
        declarations.append(f"  --okp-{name.replace('.', '-')}: {value};")
    css = ".okp-theme {\n" + "\n".join(declarations) + "\n  --okp-current-surface: var(--okp-color-surface-canvas);\n  --okp-current-text-primary: var(--okp-color-on-surface-canvas-primary);\n  --okp-current-text-secondary: var(--okp-color-on-surface-canvas-secondary);\n  --okp-current-border: var(--okp-color-border-canvas);\n  background-color: var(--okp-current-surface);\n  color: var(--okp-current-text-primary);\n  font-family: var(--okp-type-body-font-family);\n  font-size: var(--okp-type-body-font-size);\n}\n"
    for prop in ("font-weight", "line-height"):
        if f"type.body.{prop}" in resolved:
            css += f".okp-theme {{ {prop}: var(--okp-type-body-{prop}); }}\n"
    for role in selected_roles:
        props = []
        for prop in TYPE_PROPERTIES:
            name = f"type.{role}.{prop}"
            if name not in resolved: continue
            var = f"var(--okp-type-{role}-{prop})"
            if prop in ("font-size", "letter-spacing"):
                var = f"calc({var} * var(--okp-runtime-fit-scale, 1))"
            props.append(f"  {'margin-block-end' if prop == 'paragraph-gap' else prop}: {var};")
        css += f'.okp-theme [data-text-role="{role}"] {{\n' + "\n".join(props) + "\n}\n"
    def surface_css(selector, name):
        selected = resolved.get(name, "inherit")
        if selected == "inherit": return ""
        require("color.surface." + selected in resolved, "SURFACE_PAIR_INCOMPLETE: " + selected)
        aliases = {"surface": f"color.surface.{selected}", "text-primary": f"color.on-surface.{selected}.primary", "text-secondary": f"color.on-surface.{selected}.secondary", "border": f"color.border.{selected}"}
        pairs = "; ".join(f"--okp-current-{key}: var(--okp-{value.replace('.', '-')})" for key, value in aliases.items())
        return selector + " { " + pairs + "; background-color: var(--okp-current-surface); color: var(--okp-current-text-primary); }\n"
    css += surface_css('.okp-theme [data-component="card"]', "component.card.surface-role")
    css += surface_css('.okp-theme [data-component="table"] th', "component.table.header-surface-role")
    def bind_component(selector, properties):
        values = [f"{prop}: var(--okp-{name.replace('.', '-')})" for prop, name in properties.items() if name in resolved]
        return selector + " { " + "; ".join(values) + "; }\n" if values else ""
    card_selector = '.okp-theme [data-component="card"]'
    table_selector = '.okp-theme [data-component="table"] th, .okp-theme [data-component="table"] td'
    css += bind_component(card_selector, {"padding": "component.card.padding", "border-width": "component.card.border-width", "border-color": "component.card.border-color", "border-radius": "component.card.radius"})
    css += bind_component(table_selector, {"padding": "component.table.cell-padding", "border-bottom-width": "component.table.rule-width", "border-bottom-color": "component.table.rule-color"})
    # Low-priority structural fallbacks must not reset existing user component CSS.
    if "component.card.border-width" in resolved:
        css += ':where(.okp-theme [data-component="card"]) { border-style: solid; }\n'
    if "component.table.rule-width" in resolved:
        css += ':where(.okp-theme [data-component="table"] th, .okp-theme [data-component="table"] td) { border-bottom-style: solid; border-bottom-color: var(--okp-current-border); }\n'
    for edge in ("top", "right", "bottom", "left"):
        for selector, name in (("[data-component=card]", "component.card.padding-"), ("[data-component=table] th, .okp-theme [data-component=table] td", "component.table.cell-padding-")):
            if name + edge in resolved:
                css_name = (name + edge).replace(".", "-")
                css += f'.okp-theme {selector} {{ padding-{edge}: var(--okp-{css_name}); }}\n'
    css += ':where(.okp-theme [data-component="connector"] path) { fill: none; stroke: currentColor; stroke-width: 1; }\n'
    css += bind_component('.okp-theme [data-component="connector"] path', {"stroke": "component.connector.color", "stroke-width": "component.connector.stroke-width"})
    css += '.okp-theme [data-text-role="caption"] { color: var(--okp-current-text-secondary); }\n'
    scoped_lines = []
    for line in css.splitlines():
        if line.startswith((".okp-theme", ":where(.okp-theme")):
            selector, brace, declarations = line.partition("{")
            line = selector.replace(".okp-theme", scope) + brace + declarations
        scoped_lines.append(line)
    css = "\n".join(scoped_lines) + "\n"
    return css, {"contractVersion": "1.0.0", "scope": scope, "roleMap": role_map, "inferredTokens": inferred, "resolved": resolved, "origins": origins, "profile": profile, "surface": surface, "unobservedComponents": [component for component in ("card", "table", "connector") if not any(name.startswith(f"component.{component}.") for name in tokens)], "limitations": ["No automatic semantic-role classifier", "No full source style or component reconstruction", "No font availability or visual validation"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--css", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--roles", help="Comma-separated roles used by selected layouts")
    parser.add_argument("--profile")
    parser.add_argument("--surface")
    args = parser.parse_args()
    css, report = compile_theme(json.loads(Path(args.input).read_text()), args.roles.split(",") if args.roles else None, args.profile, args.surface)
    for file in (args.css, args.report): Path(file).parent.mkdir(parents=True, exist_ok=True)
    Path(args.css).write_text(css)
    Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"css": args.css, "report": args.report, "inferredCount": len(report["inferredTokens"])}))


if __name__ == "__main__":
    main()
