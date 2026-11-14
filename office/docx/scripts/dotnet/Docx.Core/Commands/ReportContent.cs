using System.Globalization;
using System.Text.Json;
using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;
using Docx.Core.Samples;

namespace Docx.Core.Commands;

internal sealed class ReportContent(IEnumerable<ReportContent.Block> blocks)
{
    internal abstract record Block;
    private sealed record Heading(string Text, int Level) : Block;
    private sealed record ParagraphText(string Text) : Block;
    private sealed record PageBreak : Block;
    private sealed record ReportTable(string[] Headers, string[][] Rows) : Block;
    private sealed record ReportList(string[] Items, bool Ordered) : Block;
    private sealed record ReportImage(string Path, int Width, int Height, string Caption, string? Alt) : Block;

    public static ReportContent Read(string? path)
    {
        if (path is null)
            return new([]);

        using var json = JsonDocument.Parse(File.ReadAllBytes(path));
        if (json.RootElement.ValueKind != JsonValueKind.Array)
            throw new FormatException("Expected an array of content blocks.");

        var directory = Path.GetDirectoryName(Path.GetFullPath(path))!;
        var content = new List<Block>();
        foreach (var item in json.RootElement.EnumerateArray())
        {
            if (item.ValueKind != JsonValueKind.Object)
                throw new FormatException($"Block {content.Count + 1} must be an object.");

            try
            {
                content.Add(ReadBlock(item, directory));
            }
            catch (Exception ex) when (ex is FormatException or InvalidOperationException or KeyNotFoundException or ArgumentException)
            {
                throw new FormatException($"Block {content.Count + 1}: {ex.Message}", ex);
            }
        }
        return new(content);
    }

    private static Block ReadBlock(JsonElement item, string directory) => RequiredText(item, "type") switch
    {
        "heading" => new Heading(RequiredText(item, "text"), item.TryGetProperty("level", out var level) ? Math.Clamp(level.GetInt32(), 1, 6) : 1),
        "paragraph" => new ParagraphText(RequiredText(item, "text")),
        "pagebreak" => new PageBreak(),
        "table" => ReadTable(item),
        "list" => new ReportList(ReadStrings(item.GetProperty("items")), item.TryGetProperty("ordered", out var ordered) && ordered.GetBoolean()),
        "image" => ReadImage(item, directory),
        var type => throw new FormatException($"Unsupported block type '{type}'."),
    };

    private static string RequiredText(JsonElement value, string key) =>
        value.GetProperty(key).GetString() ?? throw new FormatException($"'{key}' must be a string.");

    private static string[] ReadStrings(JsonElement array) => array.EnumerateArray()
        .Select(x => x.GetString() ?? throw new FormatException("Expected a string."))
        .ToArray();

    private static ReportTable ReadTable(JsonElement item)
    {
        var headers = ReadStrings(item.GetProperty("headers"));
        var rows = item.GetProperty("rows").EnumerateArray().Select(ReadStrings).ToArray();
        if (headers.Length == 0 || rows.Any(row => row.Length != headers.Length))
            throw new FormatException("A table needs at least one header and the same number of cells in each row.");
        return new(headers, rows);
    }

    private static ReportImage ReadImage(JsonElement item, string directory)
    {
        var path = Path.GetFullPath(RequiredText(item, "path"), directory);
        var width = item.GetProperty("widthPx").GetInt32();
        var height = item.GetProperty("heightPx").GetInt32();
        if (width <= 0 || height <= 0)
            throw new FormatException("Image dimensions must be positive.");

        using var stream = File.OpenRead(path);
        Span<byte> signature = stackalloc byte[8];
        var read = stream.Read(signature);
        var isPng = read == 8 && signature.SequenceEqual(new byte[] { 137, 80, 78, 71, 13, 10, 26, 10 });
        var isJpeg = read >= 3 && signature[0] == 255 && signature[1] == 216 && signature[2] == 255;
        var extension = Path.GetExtension(path).ToLowerInvariant();
        if (!(extension == ".png" && isPng) && !(extension is ".jpg" or ".jpeg" && isJpeg))
            throw new FormatException("Use a PNG or JPEG image whose bytes match its extension.");

        return new(path, width, height, RequiredText(item, "caption"),
            item.TryGetProperty("alt", out var alt) ? alt.GetString() : null);
    }

    public void AppendTo(MainDocumentPart mainPart, Body body, int contentWidthDxa)
    {
        uint imageId = 0;
        int listId = 0;
        foreach (var block in blocks)
        {
            switch (block)
            {
                case Heading heading:
                    body.Append(new Paragraph(
                        new ParagraphProperties(new ParagraphStyleId { Val = $"Heading{heading.Level}" }),
                        TextRun(heading.Text)));
                    break;
                case ParagraphText paragraph:
                    body.Append(new Paragraph(TextRun(paragraph.Text)));
                    break;
                case PageBreak:
                    body.Append(new Paragraph(new Run(new Break { Type = BreakValues.Page })));
                    break;
                case ReportTable table:
                    var element = TableSamples.CreateSimpleTable(body, table.Headers, table.Rows);
                    foreach (var column in element.GetFirstChild<TableGrid>()!.Elements<GridColumn>())
                        column.Width = (contentWidthDxa / table.Headers.Length).ToString(CultureInfo.InvariantCulture);
                    var first = true;
                    foreach (var row in element.Elements<TableRow>())
                    {
                        var properties = new TableRowProperties(new CantSplit());
                        if (first)
                            properties.Append(new TableHeader());
                        row.PrependChild(properties);
                        first = false;
                    }
                    break;
                case ReportList list:
                    AppendList(mainPart, body, list, ++listId);
                    break;
                case ReportImage image:
                    AppendImage(mainPart, body, image, ++imageId, contentWidthDxa);
                    break;
            }
        }
    }

    private static void AppendList(MainDocumentPart mainPart, Body body, ReportList list, int id)
    {
        var part = mainPart.NumberingDefinitionsPart ?? mainPart.AddNewPart<NumberingDefinitionsPart>();
        var numbering = part.Numbering ??= new Numbering();
        var definition = new AbstractNum(
            new MultiLevelType { Val = MultiLevelValues.SingleLevel },
            new Level(
                new StartNumberingValue { Val = 1 },
                new NumberingFormat { Val = list.Ordered ? NumberFormatValues.Decimal : NumberFormatValues.Bullet },
                new LevelText { Val = list.Ordered ? "%1." : "•" },
                new LevelJustification { Val = LevelJustificationValues.Left },
                new PreviousParagraphProperties(new Indentation { Left = "480", Hanging = "240" }))
            { LevelIndex = 0 })
        { AbstractNumberId = id };
        var firstInstance = numbering.GetFirstChild<NumberingInstance>();
        if (firstInstance is null)
            numbering.Append(definition);
        else
            numbering.InsertBefore(definition, firstInstance);
        numbering.Append(new NumberingInstance(new AbstractNumId { Val = id }) { NumberID = id });

        foreach (var item in list.Items)
            body.Append(new Paragraph(
                new ParagraphProperties(new NumberingProperties(
                    new NumberingLevelReference { Val = 0 }, new NumberingId { Val = id })),
                TextRun(item)));
    }

    private static void AppendImage(MainDocumentPart mainPart, Body body, ReportImage image, uint id, int contentWidthDxa)
    {
        var type = Path.GetExtension(image.Path).Equals(".png", StringComparison.OrdinalIgnoreCase)
            ? ImagePartType.Png : ImagePartType.Jpeg;
        var part = mainPart.AddImagePart(type);
        using (var source = File.OpenRead(image.Path))
            part.FeedData(source);

        const long emuPerPixel = 9525;
        const long emuPerDxa = 635;
        var width = Math.Min(image.Width * emuPerPixel, contentWidthDxa * emuPerDxa);
        var height = Math.Max(1L, (long)((double)width * image.Height / image.Width));
        var drawing = ImageSamples.BuildDrawingElement(mainPart.GetIdOfPart(part), width, height,
            id, Path.GetFileName(image.Path), image.Alt);
        body.Append(new Paragraph(new ParagraphProperties(new KeepNext()), new Run(drawing)));
        body.Append(new Paragraph(new Run(new RunProperties(new Italic()),
            new Text(image.Caption) { Space = SpaceProcessingModeValues.Preserve })));
    }

    private static Run TextRun(string text) =>
        new(new Text(text) { Space = SpaceProcessingModeValues.Preserve });
}
