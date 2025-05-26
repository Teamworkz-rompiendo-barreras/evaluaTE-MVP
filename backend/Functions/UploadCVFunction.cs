using System.IO;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.Extensions.Logging;

public static class UploadCV
{
    [FunctionName("UploadCV")]
    public static async Task<IActionResult> Run(
        [HttpTrigger(AuthorizationLevel.Function, "post", Route = null)] HttpRequest req,
        ILogger log)
    {
        log.LogInformation("Procesando la subida de un CV...");

        var form = await req.ReadFormAsync();
        var file = form.Files["file"];

        if (file == null || file.Length == 0)
            return new BadRequestObjectResult("No se adjuntó ningún archivo.");

        var filePath = Path.Combine(Path.GetTempPath(), file.FileName);

        using (var stream = new FileStream(filePath, FileMode.Create))
        {
            await file.CopyToAsync(stream);
        }

        log.LogInformation($"Archivo {file.FileName} guardado en {filePath}");
        return new OkObjectResult($"Archivo {file.FileName} recibido correctamente.");
    }
}

