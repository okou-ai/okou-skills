using System.Text.Json;
using System.Xml;
using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;
using Docx.Core.Samples;

namespace Docx.Core.Commands;

internal static class CreateContent
{
    private const double DxaPerPixel = 1440.0 / 96.0;

    internal static void Append(MainDocumentPart mainPart, Body body, string path, int widthDxa, int heightDxa)
    {
        string directory = Path.GetDirectoryName(Path.GetFullPath(path))!;
        using var content = JsonDocument.Parse(File.ReadAllText(path));
        foreach (var (block, index) in ReadArray(content.RootElement, "content").Select((block, index) => (block, index)))
        {
            try
            {
                if (block.ValueKind != JsonValueKind.Object)
                    throw new InvalidDataException("Expected an object.");

                var kind = Required(block, "type");
                string type = kind.ValueKind == JsonValueKind.Null ? "paragraph" : ReadString(kind, "type");
                switch (type)
                {
                    case "heading":
                        int level = block.TryGetProperty("level", out var value) ? ReadInt(value, "level") : 1;
                        body.Append(new Paragraph(
                            new ParagraphProperties(new ParagraphStyleId { Val = $"Heading{Math.Clamp(level, 1, 6)}" }),
                            new Run(new Text(ReadBlockText(block)))));
                        break;
                    case "paragraph":
                        body.Append(new Paragraph(new Run(new Text(ReadBlockText(block)))));
                        break;
                    case "pagebreak":
                        body.Append(new Paragraph(new Run(new Break { Type = BreakValues.Page })));
                        break;
                    case "table":
                        AppendTable(body, block, widthDxa);
                        break;
                    case "list":
                        string[] items = ReadStrings(Required(block, "items"), "items");
                        if (items.Length == 0)
                            throw new InvalidDataException("'items' must contain at least one item.");
                        bool ordered = block.TryGetProperty("ordered", out var flag) && (flag.ValueKind switch
                        {
                            JsonValueKind.True => true,
                            JsonValueKind.False => false,
                            _ => throw new InvalidDataException("'ordered' must be a boolean.")
                        });
                        ListAndNumberingSamples.AppendList(mainPart, body, items, ordered);
                        break;
                    case "image":
                        double maxWidthPx = widthDxa / DxaPerPixel;
                        double maxHeightPx = heightDxa / DxaPerPixel;
                        AppendImage(mainPart, body, block, directory, maxWidthPx, maxHeightPx);
                        break;
                    default:
                        throw new InvalidDataException($"Unknown type '{type}'.");
                }
            }
            catch (Exception ex) when (ex is InvalidDataException or ArgumentException or IOException
                or UnauthorizedAccessException or NotSupportedException or XmlException)
            {
                throw new InvalidDataException($"Content block {index + 1}: {ex.Message}", ex);
            }
        }
    }

    private static void AppendTable(Body body, JsonElement block, int widthDxa)
    {
        string[] headers = ReadStrings(Required(block, "headers"), "headers");
        if (headers.Length == 0)
            throw new InvalidDataException("'headers' must contain at least one column.");

        var rows = ReadArray(Required(block, "rows"), "rows")
            .Select((row, index) => ReadStrings(row, $"rows[{index}]")).ToArray();
        for (int index = 0; index < rows.Length; index++)
        {
            if (rows[index].Length != headers.Length)
                throw new InvalidDataException($"'rows[{index}]' must have {headers.Length} cells to match 'headers'.");
        }

        TableSamples.CreateSimpleTable(body, headers, rows, widthDxa);
    }

    private static void AppendImage(MainDocumentPart mainPart, Body body, JsonElement block, string directory,
        double maxWidthPx, double maxHeightPx)
    {
        string path = ReadString(Required(block, "path"), "path");
        int width = ReadInt(Required(block, "widthPx"), "widthPx");
        int height = ReadInt(Required(block, "heightPx"), "heightPx");
        if (width <= 0 || height <= 0)
            throw new InvalidDataException("'widthPx' and 'heightPx' must be positive integers.");

        string? caption = block.TryGetProperty("caption", out var label) ? ReadString(label, "caption") : null;
        string? alt = block.TryGetProperty("alt", out var description) ? ReadString(description, "alt") : null;
        double scale = Math.Min(1.0, Math.Min(maxWidthPx / width, maxHeightPx / height));
        var picture = ImageSamples.InsertInlineImage(mainPart, body, Path.GetFullPath(path, directory),
            Math.Max(1, (int)(width * scale)), Math.Max(1, (int)(height * scale)), alt);
        if (!string.IsNullOrEmpty(caption))
        {
            picture.PrependChild(new ParagraphProperties(new KeepNext()));
            body.Append(new Paragraph(new ParagraphProperties(new KeepLines()),
                new Run(new RunProperties(new Italic()), new Text(caption) { Space = SpaceProcessingModeValues.Preserve })));
        }
    }

    private static string ReadBlockText(JsonElement block)
    {
        var value = Required(block, "text");
        return value.ValueKind == JsonValueKind.Null ? "" : ReadString(value, "text");
    }

    private static JsonElement Required(JsonElement block, string field) =>
        block.TryGetProperty(field, out var value) ? value : throw new InvalidDataException($"'{field}' is required.");

    private static JsonElement.ArrayEnumerator ReadArray(JsonElement value, string field) =>
        value.ValueKind == JsonValueKind.Array ? value.EnumerateArray()
            : throw new InvalidDataException($"'{field}' must be an array.");

    private static string[] ReadStrings(JsonElement value, string field) =>
        ReadArray(value, field).Select((item, index) => ReadString(item, $"{field}[{index}]")).ToArray();

    private static int ReadInt(JsonElement value, string field) =>
        value.ValueKind == JsonValueKind.Number && value.TryGetInt32(out int number) ? number
            : throw new InvalidDataException($"'{field}' must be an integer.");

    private static string ReadString(JsonElement value, string field) =>
        value.ValueKind == JsonValueKind.String ? XmlConvert.VerifyXmlChars(value.GetString()!)
            : throw new InvalidDataException($"'{field}' must be a string.");
}
