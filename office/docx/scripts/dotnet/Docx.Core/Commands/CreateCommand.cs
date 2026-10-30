using System.CommandLine;
using System.Text.Json;
using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;
using Docx.Core.OpenXml;
using Docx.Core.Typography;

namespace Docx.Core.Commands;

/// <summary>
/// Scenario A: Create a new DOCX document from scratch with proper styles, sections,
/// headers/footers, and typography defaults.
/// </summary>
public static class CreateCommand
{
    public static Command Create()
    {
        var outputOption = new Option<string>("--output") { Description = "Output DOCX file path", Required = true };
        var typeOption = new Option<string>("--type") { Description = "Document type: report, letter, memo, academic" };
        typeOption.DefaultValueFactory = _ => "report";
        var titleOption = new Option<string>("--title") { Description = "Document title" };
        var authorOption = new Option<string>("--author") { Description = "Document author" };
        var pageSizeOption = new Option<string>("--page-size") { Description = "Page size: letter, a4, legal, a3" };
        pageSizeOption.DefaultValueFactory = _ => "letter";
        var marginsOption = new Option<string>("--margins") { Description = "Margin preset: standard, narrow, wide" };
        marginsOption.DefaultValueFactory = _ => "standard";
        var headerTextOption = new Option<string>("--header") { Description = "Header text" };
        var footerTextOption = new Option<string>("--footer") { Description = "Footer text" };
        var pageNumbersOption = new Option<bool>("--page-numbers") { Description = "Add page numbers in footer" };
        var tocOption = new Option<bool>("--toc") { Description = "Insert table of contents placeholder" };
        var contentJsonOption = new Option<string>("--content-json") { Description = "Path to JSON file describing document content" };

        var cmd = new Command("create", "Create a new DOCX document from scratch")
        {
            outputOption, typeOption, titleOption, authorOption, pageSizeOption,
            marginsOption, headerTextOption, footerTextOption, pageNumbersOption,
            tocOption, contentJsonOption
        };

        cmd.SetAction((parseResult) =>
        {
            var output = parseResult.GetValue(outputOption)!;
            var docType = parseResult.GetValue(typeOption) ?? "report";
            var title = parseResult.GetValue(titleOption);
            var author = parseResult.GetValue(authorOption);
            var pageSizeName = parseResult.GetValue(pageSizeOption) ?? "letter";
            var marginsName = parseResult.GetValue(marginsOption) ?? "standard";
            var headerText = parseResult.GetValue(headerTextOption);
            var footerText = parseResult.GetValue(footerTextOption);
            var pageNumbers = parseResult.GetValue(pageNumbersOption);
            var tocPlaceholder = parseResult.GetValue(tocOption);
            var contentJson = parseResult.GetValue(contentJsonOption);

            List<ContentBlock> content;
            try
            {
                content = string.IsNullOrEmpty(contentJson) ? new() : ReadContent(contentJson);
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or JsonException)
            {
                Console.Error.WriteLine($"Could not read content JSON: {ex.Message}");
                return 1;
            }

            var fontConfig = GetFontConfig(docType);
            var pageSize = GetPageSizeConfig(pageSizeName);
            var margins = GetMargins(marginsName);

            using var doc = WordprocessingDocument.Create(output, WordprocessingDocumentType.Document);
            var mainPart = doc.AddMainDocumentPart();
            mainPart.Document = new Document(new Body());
            var body = mainPart.Document.Body!;

            // Add styles part with defaults
            AddDefaultStyles(mainPart, fontConfig);

            // Add section properties (page size, margins)
            var sectPr = new SectionProperties();

            // Add header if requested
            if (!string.IsNullOrEmpty(headerText))
            {
                var headerPart = mainPart.AddNewPart<HeaderPart>();
                headerPart.Header = new Header(
                    new Paragraph(new Run(new Text(headerText))));
                var headerRefId = mainPart.GetIdOfPart(headerPart);
                sectPr.Append(new HeaderReference
                {
                    Type = HeaderFooterValues.Default,
                    Id = headerRefId
                });
            }

            // Add footer if requested
            if (!string.IsNullOrEmpty(footerText) || pageNumbers)
            {
                var footerPart = mainPart.AddNewPart<FooterPart>();
                var footerParagraph = new Paragraph();

                if (!string.IsNullOrEmpty(footerText))
                {
                    footerParagraph.Append(new Run(new Text(footerText)));
                }

                if (pageNumbers)
                {
                    if (!string.IsNullOrEmpty(footerText))
                        footerParagraph.Append(new Run(new Text(" — ") { Space = SpaceProcessingModeValues.Preserve }));

                    footerParagraph.Append(new Run(
                        new FieldChar { FieldCharType = FieldCharValues.Begin }));
                    footerParagraph.Append(new Run(
                        new FieldCode(" PAGE ") { Space = SpaceProcessingModeValues.Preserve }));
                    footerParagraph.Append(new Run(
                        new FieldChar { FieldCharType = FieldCharValues.End }));
                }

                footerPart.Footer = new Footer(footerParagraph);
                var footerRefId = mainPart.GetIdOfPart(footerPart);
                sectPr.Append(new FooterReference
                {
                    Type = HeaderFooterValues.Default,
                    Id = footerRefId
                });
            }

            // Header/footer references must precede page geometry in sectPr.
            sectPr.Append(new DocumentFormat.OpenXml.Wordprocessing.PageSize
            {
                Width = (UInt32Value)(uint)pageSize.WidthDxa,
                Height = (UInt32Value)(uint)pageSize.HeightDxa
            });
            sectPr.Append(new PageMargin
            {
                Top = margins.TopDxa,
                Bottom = margins.BottomDxa,
                Left = (UInt32Value)(uint)margins.LeftDxa,
                Right = (UInt32Value)(uint)margins.RightDxa
            });

            // Title
            if (!string.IsNullOrEmpty(title))
            {
                var titlePara = new Paragraph(
                    new ParagraphProperties(new ParagraphStyleId { Val = "Title" }),
                    new Run(new Text(title)));
                body.Append(titlePara);
            }

            // Author subtitle
            if (!string.IsNullOrEmpty(author))
            {
                var authorPara = new Paragraph(
                    new ParagraphProperties(new ParagraphStyleId { Val = "Subtitle" }),
                    new Run(new Text(author)));
                body.Append(authorPara);
            }

            // TOC placeholder
            if (tocPlaceholder)
            {
                body.Append(new Paragraph(
                    new ParagraphProperties(new ParagraphStyleId { Val = "TOCHeading" }),
                    new Run(new Text("Table of Contents"))));

                // Insert TOC field
                var tocPara = new Paragraph();
                tocPara.Append(new Run(new FieldChar { FieldCharType = FieldCharValues.Begin }));
                tocPara.Append(new Run(new FieldCode(" TOC \\o \"1-3\" \\h \\z \\u ") { Space = SpaceProcessingModeValues.Preserve }));
                tocPara.Append(new Run(new FieldChar { FieldCharType = FieldCharValues.Separate }));
                tocPara.Append(new Run(new Text("Update this field to generate table of contents.")));
                tocPara.Append(new Run(new FieldChar { FieldCharType = FieldCharValues.End }));
                body.Append(tocPara);

                // Page break after TOC
                body.Append(new Paragraph(new Run(new Break { Type = BreakValues.Page })));
            }

            // Content from JSON (if provided)
            AddContent(body, content);

            // Ensure body has at least one paragraph
            if (!body.Elements<Paragraph>().Any())
            {
                body.Append(new Paragraph());
            }

            // sectPr must be the last child of body
            body.Append(sectPr);

            mainPart.Document.Save();
            Console.WriteLine($"Created {docType} document: {output}");
            return 0;
        });

        return cmd;
    }

    private static FontConfig GetFontConfig(string docType) => docType.ToLowerInvariant() switch
    {
        "letter" => FontDefaults.Letter,
        "memo" => FontDefaults.Memo,
        "academic" => FontDefaults.Academic,
        _ => FontDefaults.Report,
    };

    private static Typography.PageSize GetPageSizeConfig(string name) => name.ToLowerInvariant() switch
    {
        "a4" => PageSizes.A4,
        "legal" => PageSizes.Legal,
        "a3" => PageSizes.A3,
        _ => PageSizes.Letter,
    };

    private static MarginConfig GetMargins(string name) => name.ToLowerInvariant() switch
    {
        "narrow" => PageSizes.NarrowMargins,
        "wide" => PageSizes.WideMargins,
        _ => PageSizes.StandardMargins,
    };

    private static void AddDefaultStyles(MainDocumentPart mainPart, FontConfig fontConfig)
    {
        var stylesPart = mainPart.AddNewPart<StyleDefinitionsPart>();
        var styles = new Styles();

        // Default run properties
        var defaultRPr = new StyleRunProperties(
            new RunFonts { Ascii = fontConfig.BodyFont, HighAnsi = fontConfig.BodyFont },
            new FontSize { Val = UnitConverter.FontSizeToSz(fontConfig.BodySize) },
            new FontSizeComplexScript { Val = UnitConverter.FontSizeToSz(fontConfig.BodySize) });

        // Normal style
        styles.Append(new Style(
            new StyleName { Val = "Normal" },
            new PrimaryStyle(),
            defaultRPr)
        { Type = StyleValues.Paragraph, StyleId = "Normal", Default = true });

        // Heading styles 1-6
        double[] headingSizes = [fontConfig.Heading1Size, fontConfig.Heading2Size, fontConfig.Heading3Size,
                                 fontConfig.Heading4Size, fontConfig.Heading5Size, fontConfig.Heading6Size];
        for (int i = 0; i < 6; i++)
        {
            var level = i + 1;
            var headingStyle = new Style(
                new StyleName { Val = $"heading {level}" },
                new BasedOn { Val = "Normal" },
                new NextParagraphStyle { Val = "Normal" },
                new PrimaryStyle(),
                new StyleParagraphProperties(
                    new KeepNext(),
                    new KeepLines(),
                    new SpacingBetweenLines { Before = "240", After = "120" },
                    new OutlineLevel { Val = i }),
                new StyleRunProperties(
                    new RunFonts { Ascii = fontConfig.HeadingFont, HighAnsi = fontConfig.HeadingFont },
                    new Bold(),
                    new FontSize { Val = UnitConverter.FontSizeToSz(headingSizes[i]) },
                    new FontSizeComplexScript { Val = UnitConverter.FontSizeToSz(headingSizes[i]) }))
            { Type = StyleValues.Paragraph, StyleId = $"Heading{level}" };
            styles.Append(headingStyle);
        }

        // Title style
        styles.Append(new Style(
            new StyleName { Val = "Title" },
            new BasedOn { Val = "Normal" },
            new NextParagraphStyle { Val = "Normal" },
            new PrimaryStyle(),
            new StyleParagraphProperties(
                new SpacingBetweenLines { After = "300" },
                new Justification { Val = JustificationValues.Center }),
            new StyleRunProperties(
                new RunFonts { Ascii = fontConfig.HeadingFont, HighAnsi = fontConfig.HeadingFont },
                new FontSize { Val = UnitConverter.FontSizeToSz(fontConfig.Heading1Size + 6) },
                new FontSizeComplexScript { Val = UnitConverter.FontSizeToSz(fontConfig.Heading1Size + 6) }))
        { Type = StyleValues.Paragraph, StyleId = "Title" });

        // Subtitle style
        styles.Append(new Style(
            new StyleName { Val = "Subtitle" },
            new BasedOn { Val = "Normal" },
            new NextParagraphStyle { Val = "Normal" },
            new StyleParagraphProperties(
                new SpacingBetweenLines { After = "200" },
                new Justification { Val = JustificationValues.Center }),
            new StyleRunProperties(
                new Color { Val = "5A5A5A" },
                new FontSize { Val = UnitConverter.FontSizeToSz(fontConfig.BodySize + 2) }))
        { Type = StyleValues.Paragraph, StyleId = "Subtitle" });

        stylesPart.Styles = styles;
        stylesPart.Styles.Save();
    }

    private record ContentBlock(string Type, string Text, int Level);

    private static List<ContentBlock> ReadContent(string path)
    {
        using var json = JsonDocument.Parse(File.ReadAllText(path));
        if (json.RootElement.ValueKind != JsonValueKind.Array)
            throw new JsonException("Content must be an array of blocks.");

        var content = new List<ContentBlock>();
        foreach (var element in json.RootElement.EnumerateArray())
        {
            var index = content.Count + 1;
            if (element.ValueKind != JsonValueKind.Object
                || !element.TryGetProperty("type", out var typeElement) || typeElement.ValueKind != JsonValueKind.String
                || !element.TryGetProperty("text", out var textElement) || textElement.ValueKind != JsonValueKind.String)
                throw new JsonException($"Content block {index} requires string 'type' and 'text' fields.");

            var type = typeElement.GetString()!;
            var text = textElement.GetString()!;
            if (type is not ("heading" or "paragraph" or "pagebreak"))
                throw new JsonException($"Unsupported content type '{type}' in block {index}.");

            var level = 1;
            if (type == "heading" && element.TryGetProperty("level", out var levelElement)
                && (levelElement.ValueKind != JsonValueKind.Number || !levelElement.TryGetInt32(out level)))
                throw new JsonException($"Heading level in block {index} must be an integer.");

            content.Add(new ContentBlock(type, text, Math.Clamp(level, 1, 6)));
        }
        return content;
    }

    private static void AddContent(Body body, IEnumerable<ContentBlock> content)
    {
        foreach (var block in content)
        {
            switch (block.Type)
            {
                case "heading":
                    body.Append(new Paragraph(
                        new ParagraphProperties(new ParagraphStyleId { Val = $"Heading{block.Level}" }),
                        new Run(new Text(block.Text))));
                    break;
                case "paragraph":
                    body.Append(new Paragraph(new Run(new Text(block.Text))));
                    break;
                case "pagebreak":
                    body.Append(new Paragraph(new Run(new Break { Type = BreakValues.Page })));
                    break;
            }
        }
    }
}
