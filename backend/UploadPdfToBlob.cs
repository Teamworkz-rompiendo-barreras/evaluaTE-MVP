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
        // 1. Comprueba que hay un archivo adjunto
        var form = await req.ReadFormAsync();
        var file = form.Files["file"];
        if (file == null || file.Length == 0)
        {
            return new BadRequestObjectResult("No se ha enviado ningún archivo.");
        }

        // 2. Nombre del blob (puedes personalizarlo, aquí uso el nombre original)
        string blobName = file.FileName;

        // 3. Obtén la cadena de conexión del settings
        string connectionString = Environment.GetEnvironmentVariable("AzureWebJobsStorage");

        // 4. Crea el cliente Blob y sube el archivo
        var blobClient = new BlobContainerClient(connectionString, "cvs"); // Usa el nombre de tu contenedor aquí
        await blobClient.CreateIfNotExistsAsync();
        var blob = blobClient.GetBlobClient(blobName);

        using (var stream = file.OpenReadStream())
        {
            await blob.UploadAsync(stream, overwrite: true);
        }

        return new OkObjectResult($"Archivo '{blobName}' subido correctamente a Blob Storage.");
    }
}
