using System;
using System.IO;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using Azure.Storage.Blobs;

public static class UploadPdfToBlob
{
    [FunctionName("UploadPdfToBlob")]
    public static async Task<IActionResult> Run(
        [HttpTrigger(AuthorizationLevel.Function, "post", Route = null)] HttpRequest req,
        ILogger log)
    {
        var form = await req.ReadFormAsync();
        var file = form.Files["file"];
        if (file == null || file.Length == 0)
        {
            return new BadRequestObjectResult("No se ha enviado ningún archivo.");
        }

        // Validar que es PDF
        if (!file.FileName.EndsWith(".pdf", StringComparison.OrdinalIgnoreCase) || file.ContentType != "application/pdf")
        {
            return new BadRequestObjectResult("Solo se permiten archivos PDF.");
        }

        // Nombre único para evitar sobrescribir archivos
        string blobName = $"{Path.GetFileNameWithoutExtension(file.FileName)}_{DateTime.UtcNow.Ticks}{Path.GetExtension(file.FileName)}";

        // Usa AzureWebJobsStorage o BlobConnectionString según tu configuración
        string connectionString = Environment.GetEnvironmentVariable("AzureWebJobsStorage");
        var blobClient = new BlobContainerClient(connectionString, "cvs");
        await blobClient.CreateIfNotExistsAsync();
        var blob = blobClient.GetBlobClient(blobName);

        using (var stream = file.OpenReadStream())
        {
            await blob.UploadAsync(stream, overwrite: true);
        }

        return new OkObjectResult(new {
            message = $"Archivo '{blobName}' subido correctamente a Blob Storage.",
            url = blob.Uri.ToString()
        });
    }
}
