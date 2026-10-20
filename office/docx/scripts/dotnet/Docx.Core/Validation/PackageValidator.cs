using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Validation;

namespace Docx.Core.Validation;

/// <summary>Validate all package parts without imposing a document style.</summary>
public class PackageValidator
{
    public ValidationResult Validate(string path)
    {
        var result = new ValidationResult();
        using var document = WordprocessingDocument.Open(path, false);
        var validator = new OpenXmlValidator(FileFormatVersions.Microsoft365);
        foreach (var error in validator.Validate(document))
        {
            result.Errors.Add(new ValidationError
            {
                Element = error.Path?.XPath ?? "",
                Message = $"{error.Part?.Uri}: {error.Description}"
            });
        }
        return result;
    }
}
