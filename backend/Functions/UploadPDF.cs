using System.IO;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

public static class UploadPDF
{
    [FunctionName("UploadPDF")]
    public static async Task<IActionResult> Run(
        [HttpTrigger(AuthorizationLevel.Function, "post", Route = null)] HttpRequest req,
        ILogger log)
    {
        // Verificamos que haya archivos en la petición
        if (!req.HasFormContentType || req.Form.Files.Count == 0)
            return new BadRequestObjectResult("No se ha recibido ningún archivo.");

        var file = req.Form.Files[0];

        if (file.Length == 0 || Path.GetExtension(file.FileName).ToLower() != ".pdf")
            return new BadRequestObjectResult("Solo se permiten archivos PDF.");

        // Guardar el archivo en disco (cambia la ruta según tu entorno)
        var outputPath = Path.Combine("C:\\AzureFunctionsUploads", file.FileName);
        Directory.CreateDirectory("C:\\AzureFunctionsUploads"); // Asegura que la carpeta exista

        using (var stream = new FileStream(outputPath, FileMode.Create))
        {
            await file.CopyToAsync(stream);
        }

        log.LogInformation($"Archivo {file.FileName} subido correctamente.");

        return new OkObjectResult($"Archivo {file.FileName} subido correctamente.");
    }
}
