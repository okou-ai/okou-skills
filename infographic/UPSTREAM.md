# Sources and attribution

This package is an Okou-native integration, not an installation of four upstream skills. It uses AntV's npm renderer and adapts a small set of content, layout, style, and review instructions. Upstream account setup, global preferences, automatic retries, publishing, and animation workflows are not imported.

| Source | Pinned source | Use in this package | License notice |
| --- | --- | --- | --- |
| AntV Infographic | [antvis/Infographic@5ae0d9394ac6280cb688eb4b4345881e291b9209](https://github.com/antvis/Infographic/tree/5ae0d9394ac6280cb688eb4b4345881e291b9209) | Native DSL, built-in templates and rendering API; npm dependency is separately pinned in `package-lock.json` | [AntV MIT](licenses/antv-MIT.txt) |
| Baoyu Infographic | [JimLiu/baoyu-skills@ca703c2d7c2c4399a1dc0cf82224f8551e05a96d](https://github.com/JimLiu/baoyu-skills/tree/ca703c2d7c2c4399a1dc0cf82224f8551e05a96d/skills/baoyu-infographic) | Layout × style method, selected handmade/flat/technical directions, exact-copy prompt preparation, and raster-review rules in `references/image.md` | [Baoyu MIT](licenses/baoyu-MIT.txt) |
| Epic Infographics | [OrRon/EpicInfographics@bf97e589df21302aacb24d9c7631393e81b9a015](https://github.com/OrRon/EpicInfographics/tree/bf97e589df21302aacb24d9c7631393e81b9a015) | Topic-specific focal point, truthful geometry and render–look–fix review instructions; its renderer and animation stack are not copied | [Epic MIT](licenses/epic-MIT.txt) |
| Infographic | [remybroun/infographic@6d0d5980ebb418fec6acae3ab19ddfbe92cdb2aa](https://github.com/remybroun/infographic/tree/6d0d5980ebb418fec6acae3ab19ddfbe92cdb2aa) | Graphic-first explanation, preserving specific facts and read-back checks; its brief/spec framework is not copied | [Remy MIT](licenses/remy-MIT.txt) |

The scripts, combined instructions, and starter examples are local integration work. Keep all notices with redistributed packages. The renderer's generated HTML embeds the installed AntV browser bundle; preserve its runtime license notice alongside delivered editable source. Third-party fonts and optional illustrations are not bundled here; only use assets whose licenses permit the intended use.
