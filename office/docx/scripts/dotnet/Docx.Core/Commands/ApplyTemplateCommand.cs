using System.CommandLine;
using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;

namespace Docx.Core.Commands;

/// <summary>
/// Scenario C: Apply formatting from a template DOCX to a source DOCX.
/// Copies styles, theme, numbering, headers/footers, and section properties
/// from the template while preserving all content from the source.
/// </summary>
public static class ApplyTemplateCommand
{
    public static Command Create()
    {
        var inputOpt = new Option<string>("--input") { Description = "Source DOCX (content to keep)", Required = true };
        var templateOpt = new Option<string>("--template") { Description = "Template DOCX (formatting to apply)", Required = true };
        var outputOpt = new Option<string>("--output") { Description = "Output DOCX file path", Required = true };
        var applyStylesOpt = new Option<bool>("--apply-styles") { Description = "Copy styles.xml from template" };
        applyStylesOpt.DefaultValueFactory = _ => true;
        var applyThemeOpt = new Option<bool>("--apply-theme") { Description = "Copy theme from template" };
        applyThemeOpt.DefaultValueFactory = _ => true;
        var applyNumberingOpt = new Option<bool>("--apply-numbering") { Description = "Copy numbering.xml from template" };
        applyNumberingOpt.DefaultValueFactory = _ => true;
        var applyHeadersFootersOpt = new Option<bool>("--apply-headers-footers") { Description = "Copy headers/footers from template" };
        var applySectionsOpt = new Option<bool>("--apply-sections") { Description = "Apply section properties from template" };
        applySectionsOpt.DefaultValueFactory = _ => true;

        var cmd = new Command("apply-template", "Apply template formatting to a DOCX")
        {
            inputOpt, templateOpt, outputOpt, applyStylesOpt, applyThemeOpt,
            applyNumberingOpt, applyHeadersFootersOpt, applySectionsOpt
        };

        cmd.SetAction((parseResult) =>
        {
            var inputPath = parseResult.GetValue(inputOpt)!;
            var templatePath = parseResult.GetValue(templateOpt)!;
            var outputPath = parseResult.GetValue(outputOpt)!;
            var applyStyles = parseResult.GetValue(applyStylesOpt);
            var applyTheme = parseResult.GetValue(applyThemeOpt);
            var applyNumbering = parseResult.GetValue(applyNumberingOpt);
            var applyHeadersFooters = parseResult.GetValue(applyHeadersFootersOpt);
            var applySections = parseResult.GetValue(applySectionsOpt);

            if (!File.Exists(inputPath)) { Console.Error.WriteLine($"Input file not found: {inputPath}"); return 1; }
            if (!File.Exists(templatePath)) { Console.Error.WriteLine($"Template file not found: {templatePath}"); return 1; }

            // Create output as a copy of the source
            File.Copy(inputPath, outputPath, overwrite: true);

            using var output = WordprocessingDocument.Open(outputPath, true);
            using var template = WordprocessingDocument.Open(templatePath, false);

            var outputMain = output.MainDocumentPart;
            var templateMain = template.MainDocumentPart;
            if (outputMain?.Document?.Body == null || templateMain?.Document?.Body == null)
            {
                Console.Error.WriteLine("Invalid document: missing main document part.");
                return 1;
            }

            int appliedCount = 0;

            if (applyStyles)
            {
                CopyStyles(templateMain, outputMain);
                appliedCount++;
                Console.WriteLine("  Applied: styles");
            }

            if (applyTheme)
            {
                CopyTheme(templateMain, outputMain);
                appliedCount++;
                Console.WriteLine("  Applied: theme");
            }

            var templateNumberingIds = new Dictionary<int, int>();
            if (applyNumbering)
            {
                templateNumberingIds = CopyNumbering(templateMain, outputMain);
                if (applyStyles && outputMain.StyleDefinitionsPart?.Styles is { } styles)
                    RemapNumberingReferences(styles, templateNumberingIds);
                appliedCount++;
                Console.WriteLine("  Applied: numbering");
            }

            if (applyHeadersFooters)
            {
                CopyHeadersAndFooters(templateMain, outputMain, templateNumberingIds);
                appliedCount++;
                Console.WriteLine("  Applied: headers/footers");
            }

            if (applySections)
            {
                CopySectionProperties(templateMain, outputMain);
                appliedCount++;
                Console.WriteLine("  Applied: section properties");
            }

            outputMain.Document.Save();
            Console.WriteLine($"Applied {appliedCount} formatting component(s) from template to {outputPath}");
            return 0;
        });

        return cmd;
    }

    /// <summary>
    /// Replaces the output's StyleDefinitionsPart with the template's version.
    /// </summary>
    private static void CopyStyles(MainDocumentPart template, MainDocumentPart output)
    {
        var templateStyles = template.StyleDefinitionsPart;
        if (templateStyles == null) return;

        if (output.StyleDefinitionsPart != null)
            output.DeletePart(output.StyleDefinitionsPart);

        var newStylesPart = output.AddNewPart<StyleDefinitionsPart>();

        using var stream = templateStyles.GetStream(FileMode.Open, FileAccess.Read);
        newStylesPart.FeedData(stream);
    }

    /// <summary>
    /// Replaces the output's ThemePart with the template's version.
    /// </summary>
    private static void CopyTheme(MainDocumentPart template, MainDocumentPart output)
    {
        var templateTheme = template.ThemePart;
        if (templateTheme == null) return;

        if (output.ThemePart != null)
            output.DeletePart(output.ThemePart);

        var newThemePart = output.AddNewPart<ThemePart>();

        using var stream = templateTheme.GetStream(FileMode.Open, FileAccess.Read);
        newThemePart.FeedData(stream);
    }

    /// <summary>
    /// Imports template numbering with fresh IDs, preserving the source's lists.
    /// </summary>
    private static Dictionary<int, int> CopyNumbering(MainDocumentPart template, MainDocumentPart output)
    {
        var templateNumbering = template.NumberingDefinitionsPart;
        if (templateNumbering?.Numbering == null) return new();

        var outputNumbering = output.NumberingDefinitionsPart;
        if (outputNumbering == null)
        {
            output.AddPart(templateNumbering);
            return new();
        }

        outputNumbering.Numbering ??= new Numbering();
        var imported = (Numbering)templateNumbering.Numbering.CloneNode(true);
        var pictureIds = RemapDefinitionIds(imported, outputNumbering.Numbering, "numPicBullet", "numPicBulletId");
        var abstractIds = RemapDefinitionIds(imported, outputNumbering.Numbering, "abstractNum", "abstractNumId");
        var numberIds = RemapDefinitionIds(imported, outputNumbering.Numbering, "num", "numId");
        foreach (var id in imported.Descendants<AbstractNumId>())
            if (id.Val?.Value is int value && abstractIds.TryGetValue(value, out var mapped))
                id.Val = mapped;
        foreach (var id in imported.Descendants().Where(e => e.LocalName == "lvlPicBulletId"))
        {
            var attribute = id.GetAttribute("val", W);
            if (int.TryParse(attribute.Value, out var value) && pictureIds.TryGetValue(value, out var mapped))
                id.SetAttribute(new OpenXmlAttribute("w", "val", W, mapped.ToString()));
        }

        var relationshipIds = new Dictionary<string, string>();
        foreach (var child in templateNumbering.Parts)
            relationshipIds[child.RelationshipId] = outputNumbering.GetIdOfPart(outputNumbering.AddPart(child.OpenXmlPart));
        foreach (var rel in templateNumbering.ExternalRelationships)
            relationshipIds[rel.Id] = outputNumbering.AddExternalRelationship(rel.RelationshipType, rel.Uri).Id;
        foreach (var rel in templateNumbering.HyperlinkRelationships)
            relationshipIds[rel.Id] = outputNumbering.AddHyperlinkRelationship(rel.Uri, rel.IsExternal).Id;
        foreach (var element in imported.Descendants())
        {
            foreach (var attribute in element.GetAttributes())
            {
                if ((attribute.NamespaceUri == "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                    || (attribute.NamespaceUri == "urn:schemas-microsoft-com:office:office" && attribute.LocalName == "relid"))
                    && attribute.Value is { } value && relationshipIds.TryGetValue(value, out var mapped))
                    element.SetAttribute(new OpenXmlAttribute(attribute.Prefix, attribute.LocalName, attribute.NamespaceUri, mapped));
            }
        }

        foreach (var definition in imported.Elements().Where(e => e.LocalName != "numIdMac"))
        {
            var following = definition.LocalName switch
            {
                "numPicBullet" => outputNumbering.Numbering.Elements().FirstOrDefault(e => e.LocalName != "numPicBullet"),
                "abstractNum" => outputNumbering.Numbering.Elements().FirstOrDefault(e => e.LocalName is "num" or "numIdMac"),
                "num" => outputNumbering.Numbering.Elements().FirstOrDefault(e => e.LocalName == "numIdMac"),
                _ => null
            };
            if (following == null)
                outputNumbering.Numbering.Append(definition.CloneNode(true));
            else
                outputNumbering.Numbering.InsertBefore(definition.CloneNode(true), following);
        }
        outputNumbering.Numbering.Save();
        return numberIds;
    }

    private const string W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main";

    private static Dictionary<int, int> RemapDefinitionIds(Numbering imported, Numbering existing, string elementName, string attributeName)
    {
        var nextId = existing.Elements().Where(e => e.LocalName == elementName)
            .Select(e => GetDefinitionId(e, attributeName)).DefaultIfEmpty(0).Max() + 1;
        var mapping = new Dictionary<int, int>();
        foreach (var element in imported.Elements().Where(e => e.LocalName == elementName))
        {
            var oldId = GetDefinitionId(element, attributeName);
            mapping[oldId] = nextId;
            element.SetAttribute(new OpenXmlAttribute("w", attributeName, W, (nextId++).ToString()));
        }
        return mapping;
    }

    private static int GetDefinitionId(OpenXmlElement element, string attributeName) =>
        int.TryParse(element.GetAttribute(attributeName, W).Value, out var id)
            ? id : throw new InvalidDataException($"Invalid {attributeName} in numbering definition {element.LocalName}");

    private static void RemapNumberingReferences(OpenXmlElement? root, IReadOnlyDictionary<int, int> mapping)
    {
        if (root == null) return;
        foreach (var id in root.Descendants<NumberingId>())
            if (id.Val?.Value is int value && mapping.TryGetValue(value, out var mapped))
                id.Val = mapped;
    }

    /// <summary>
    /// Copies headers and footers from the template, remapping relationship IDs.
    /// </summary>
    private static void CopyHeadersAndFooters(MainDocumentPart template, MainDocumentPart output, IReadOnlyDictionary<int, int> numberingIds)
    {
        var outputBody = output.Document?.Body;
        if (outputBody == null) return;

        // Remove existing header/footer parts from output
        foreach (var hp in output.HeaderParts.ToList())
            output.DeletePart(hp);
        foreach (var fp in output.FooterParts.ToList())
            output.DeletePart(fp);

        // Remove existing header/footer references from all section properties
        foreach (var sectPr in outputBody.Descendants<SectionProperties>())
        {
            foreach (var hr in sectPr.Elements<HeaderReference>().ToList())
                hr.Remove();
            foreach (var fr in sectPr.Elements<FooterReference>().ToList())
                fr.Remove();
        }

        var templateBody = template.Document?.Body;
        if (templateBody == null) return;

        var templateFinalSectPr = templateBody.Descendants<SectionProperties>().LastOrDefault();
        if (templateFinalSectPr == null) return;

        var outputFinalSectPr = outputBody.Descendants<SectionProperties>().LastOrDefault();
        if (outputFinalSectPr == null)
        {
            outputFinalSectPr = new SectionProperties();
            outputBody.Append(outputFinalSectPr);
        }

        // Copy headers
        foreach (var headerRef in templateFinalSectPr.Elements<HeaderReference>())
        {
            var templateHeaderPart = template.GetPartById(headerRef.Id!) as HeaderPart;
            if (templateHeaderPart == null) continue;

            var newHeaderPart = output.AddNewPart<HeaderPart>();
            using (var stream = templateHeaderPart.GetStream(FileMode.Open, FileAccess.Read))
            {
                newHeaderPart.FeedData(stream);
            }

            CopyPartRelationships(templateHeaderPart, newHeaderPart);
            RemapNumberingReferences(newHeaderPart.Header, numberingIds);

            var newRefId = output.GetIdOfPart(newHeaderPart);
            outputFinalSectPr.InsertAt(new HeaderReference
            {
                Type = headerRef.Type,
                Id = newRefId
            }, 0);
        }

        // Copy footers
        foreach (var footerRef in templateFinalSectPr.Elements<FooterReference>())
        {
            var templateFooterPart = template.GetPartById(footerRef.Id!) as FooterPart;
            if (templateFooterPart == null) continue;

            var newFooterPart = output.AddNewPart<FooterPart>();
            using (var stream = templateFooterPart.GetStream(FileMode.Open, FileAccess.Read))
            {
                newFooterPart.FeedData(stream);
            }

            CopyPartRelationships(templateFooterPart, newFooterPart);
            RemapNumberingReferences(newFooterPart.Footer, numberingIds);

            var newRefId = output.GetIdOfPart(newFooterPart);
            var lastHeaderRef = outputFinalSectPr.Elements<HeaderReference>().LastOrDefault();
            if (lastHeaderRef != null)
                lastHeaderRef.InsertAfterSelf(new FooterReference { Type = footerRef.Type, Id = newRefId });
            else
                outputFinalSectPr.InsertAt(new FooterReference { Type = footerRef.Type, Id = newRefId }, 0);
        }
    }

    /// <summary>
    /// Copies sub-relationships (images, etc.) from a source part to a target part.
    /// </summary>
    private static void CopyPartRelationships(OpenXmlPart source, OpenXmlPart target)
    {
        foreach (var rel in source.ExternalRelationships)
        {
            target.AddExternalRelationship(rel.RelationshipType, rel.Uri, rel.Id);
        }

        foreach (var rel in source.HyperlinkRelationships)
            target.AddHyperlinkRelationship(rel.Uri, rel.IsExternal, rel.Id);

        foreach (var childPart in source.Parts)
        {
            target.AddPart(childPart.OpenXmlPart, childPart.RelationshipId);
        }
    }

    /// <summary>
    /// Copies page size, margins, columns, and document grid from template section properties.
    /// </summary>
    private static void CopySectionProperties(MainDocumentPart template, MainDocumentPart output)
    {
        var templateBody = template.Document?.Body;
        var outputBody = output.Document?.Body;
        if (templateBody == null || outputBody == null) return;

        var templateSectPr = templateBody.Descendants<SectionProperties>().LastOrDefault();
        if (templateSectPr == null) return;

        var outputSectPr = outputBody.Descendants<SectionProperties>().LastOrDefault();
        if (outputSectPr == null)
        {
            outputSectPr = new SectionProperties();
            outputBody.Append(outputSectPr);
        }

        CopyChildElement<PageSize>(templateSectPr, outputSectPr);
        CopyChildElement<PageMargin>(templateSectPr, outputSectPr);
        CopyChildElement<Columns>(templateSectPr, outputSectPr);
        CopyChildElement<DocGrid>(templateSectPr, outputSectPr);
        CopyChildElement<PageBorders>(templateSectPr, outputSectPr);
    }

    private static void CopyChildElement<T>(SectionProperties source, SectionProperties target) where T : OpenXmlElement
    {
        var sourceElement = source.GetFirstChild<T>();
        if (sourceElement == null) return;

        var existing = target.GetFirstChild<T>();
        existing?.Remove();

        target.AddChild((T)sourceElement.CloneNode(true), true);
    }
}
