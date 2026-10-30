using System.CommandLine;
using System.IO.Compression;
using System.Text.Json;
using System.Xml.Linq;
using Docx.Core.OpenXml;

namespace Docx.Core.Commands;

public static class AnalyzeCommand
{
    private static readonly XNamespace W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main";
    private static readonly XNamespace WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing";

    public static Command Create()
    {
        var inputOption = new Option<string>("--input") { Description = "DOCX file to analyze", Required = true };
        var jsonOption = new Option<bool>("--json") { Description = "Output as JSON" };

        var cmd = new Command("analyze", "Analyze document structure and styles")
        {
            inputOption, jsonOption
        };

        cmd.SetAction((parseResult) =>
        {
            var input = parseResult.GetValue(inputOption)!;
            var asJson = parseResult.GetValue(jsonOption);

            if (!File.Exists(input))
            {
                Console.Error.WriteLine($"File not found: {input}");
                return 1;
            }

            using var zip = ZipFile.OpenRead(input);
            var doc = DocumentParts.ReadDocument(input);
            if (doc == null)
            {
                Console.Error.WriteLine("Not a valid DOCX");
                return 1;
            }

            var body = doc.Root?.Element(W + "body");
            if (body == null) return 1;

            // Sections
            var sections = body.Descendants(W + "sectPr").ToList();
            var sectionBreaks = sections.Select(s => (string?)s.Element(W + "type")?.Attribute(W + "val") ?? "nextPage").ToList();

            // Headings
            var headings = new List<object>();
            foreach (var p in body.Descendants(W + "p"))
            {
                var style = (string?)p.Element(W + "pPr")?.Element(W + "pStyle")?.Attribute(W + "val");
                if (style?.StartsWith("Heading", StringComparison.OrdinalIgnoreCase) == true)
                {
                    var text = string.Concat(p.Descendants(W + "t").Select(t => t.Value));
                    headings.Add(new { style, text });
                }
            }

            // Tables
            var tables = body.Descendants(W + "tbl").Select(tbl => new
            {
                rows = tbl.Elements(W + "tr").Count(),
                cols = tbl.Elements(W + "tr").FirstOrDefault()?.Elements(W + "tc").Count() ?? 0
            }).ToList();

            // Images
            var images = body.Descendants(W + "drawing").Count();

            // Headers/footers
            var headerRefs = sections.SelectMany(s => s.Elements(W + "headerReference")).Count();
            var footerRefs = sections.SelectMany(s => s.Elements(W + "footerReference")).Count();

            // Paragraphs and word count
            var paragraphs = body.Descendants(W + "p").ToList();
            var allText = string.Concat(body.Descendants(W + "t").Select(t => t.Value));
            var wordCount = allText.Split(new[] { ' ', '\t', '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries).Length;

            // XML file sizes
            var fileSizes = zip.Entries
                .Where(e => e.FullName.StartsWith("word/") && e.FullName.EndsWith(".xml"))
                .Select(e => new { file = e.FullName, size = e.Length })
                .OrderByDescending(e => e.size)
                .ToList();

            // Styles
            var styleNames = new List<string>();
            var stylesDoc = DocumentParts.ReadStyles(input);
            if (stylesDoc != null)
            {
                styleNames = stylesDoc.Descendants(W + "style")
                    .Where(s => (string?)s.Attribute(W + "customStyle") is "1" or "true" or "on")
                    .Select(s => (string?)s.Attribute(W + "styleId") ?? "")
                    .Where(s => s != "")
                    .ToList();
            }

            var analysis = new
            {
                sections = new { count = sections.Count, breakTypes = sectionBreaks },
                headings,
                tables = new { count = tables.Count, details = tables },
                images,
                headerFooter = new { headers = headerRefs, footers = footerRefs },
                paragraphs = paragraphs.Count,
                estimatedWordCount = wordCount,
                xmlFileSizes = fileSizes,
                customStyles = new { count = styleNames.Count, names = styleNames }
            };

            if (asJson)
            {
                Console.WriteLine(JsonSerializer.Serialize(analysis, new JsonSerializerOptions { WriteIndented = true }));
            }
            else
            {
                Console.WriteLine($"Sections:       {sections.Count} ({string.Join(", ", sectionBreaks)})");
                Console.WriteLine($"Headings:       {headings.Count}");
                foreach (var h in headings)
                    Console.WriteLine($"  {h}");
                Console.WriteLine($"Tables:         {tables.Count}");
                foreach (var t in tables)
                    Console.WriteLine($"  {t.rows} rows x {t.cols} cols");
                Console.WriteLine($"Images:         {images}");
                Console.WriteLine($"Headers:        {headerRefs}");
                Console.WriteLine($"Footers:        {footerRefs}");
                Console.WriteLine($"Paragraphs:     {paragraphs.Count}");
                Console.WriteLine($"Word count:     ~{wordCount}");
                Console.WriteLine($"Custom styles:  {styleNames.Count}");
                foreach (var s in styleNames)
                    Console.WriteLine($"  {s}");
                Console.WriteLine("XML file sizes:");
                foreach (var f in fileSizes)
                    Console.WriteLine($"  {f.file}: {f.size:N0} bytes");
            }
            return 0;
        });

        return cmd;
    }
}
