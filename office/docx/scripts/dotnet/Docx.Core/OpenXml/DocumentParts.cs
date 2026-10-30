using System.Xml.Linq;
using DocumentFormat.OpenXml.Packaging;

namespace Docx.Core.OpenXml;

internal static class DocumentParts
{
    public static XDocument? ReadDocument(string path)
    {
        using var document = WordprocessingDocument.Open(path, false);
        return ReadXml(document.MainDocumentPart);
    }

    public static XDocument? ReadStyles(string path)
    {
        using var document = WordprocessingDocument.Open(path, false);
        return ReadXml(document.MainDocumentPart?.StyleDefinitionsPart);
    }

    public static XDocument? ReadNumbering(string path)
    {
        using var document = WordprocessingDocument.Open(path, false);
        return ReadXml(document.MainDocumentPart?.NumberingDefinitionsPart);
    }

    private static XDocument? ReadXml(OpenXmlPart? part)
    {
        if (part == null) return null;
        using var stream = part.GetStream(FileMode.Open, FileAccess.Read);
        return XDocument.Load(stream);
    }
}
