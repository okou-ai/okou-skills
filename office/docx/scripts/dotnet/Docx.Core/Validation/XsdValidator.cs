using System.IO.Compression;
using System.Xml;
using System.Xml.Schema;

namespace Docx.Core.Validation;

public class XsdValidator
{
    public ValidationResult Validate(string docxPath, string xsdPath)
    {
        using var zip = ZipFile.OpenRead(docxPath);
        var entry = zip.GetEntry("word/document.xml")
            ?? throw new InvalidOperationException("DOCX does not contain word/document.xml");

        using var stream = entry.Open();
        using var reader = new StreamReader(stream);
        var xmlContent = reader.ReadToEnd();

        return ValidateXml(xmlContent, xsdPath);
    }

    public ValidationResult ValidateXml(string xmlContent, string xsdPath)
    {
        var result = new ValidationResult();
        var settings = new XmlReaderSettings();

        // Resolve imports only inside the supplied schema directory, never over HTTP.
        var schemaSet = new XmlSchemaSet
        {
            XmlResolver = new LocalSchemaResolver(Path.GetDirectoryName(Path.GetFullPath(xsdPath))!)
        };
        settings.Schemas = schemaSet;
        settings.ValidationType = ValidationType.Schema;
        settings.ValidationFlags |= XmlSchemaValidationFlags.ReportValidationWarnings;

        settings.ValidationEventHandler += (sender, e) =>
        {
            var error = new ValidationError
            {
                LineNumber = e.Exception?.LineNumber ?? 0,
                LinePosition = e.Exception?.LinePosition ?? 0,
                Message = e.Message,
                Severity = e.Severity == XmlSeverityType.Warning ? "Warning" : "Error"
            };

            if (e.Severity == XmlSeverityType.Warning)
                result.Warnings.Add(error);
            else
                result.Errors.Add(error);
        };

        try
        {
            schemaSet.Add(null, xsdPath);
            schemaSet.Compile();
            using var stringReader = new StringReader(xmlContent);
            using var xmlReader = XmlReader.Create(stringReader, settings);
            while (xmlReader.Read()) { }
        }
        catch (XmlSchemaException ex)
        {
            result.Errors.Add(new ValidationError
            {
                LineNumber = ex.LineNumber,
                LinePosition = ex.LinePosition,
                Message = $"Schema error: {ex.Message}"
            });
        }
        catch (XmlException ex)
        {
            result.Errors.Add(new ValidationError
            {
                LineNumber = ex.LineNumber,
                LinePosition = ex.LinePosition,
                Message = $"XML parse error: {ex.Message}",
                Severity = "Error"
            });
        }

        return result;
    }

    private sealed class LocalSchemaResolver(string directory) : XmlUrlResolver
    {
        public override object GetEntity(Uri absoluteUri, string? role, Type? ofObjectToReturn)
        {
            var relative = absoluteUri.IsFile
                ? Path.GetRelativePath(directory, absoluteUri.LocalPath)
                : "..";
            if (Path.IsPathRooted(relative) || relative == ".." ||
                relative.StartsWith(".." + Path.DirectorySeparatorChar))
                throw new XmlSchemaException("Schema imports must stay in the local schema directory.");
            return File.OpenRead(absoluteUri.LocalPath);
        }
    }
}
