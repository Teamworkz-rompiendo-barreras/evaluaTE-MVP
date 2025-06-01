using System.IO;
using System.Threading.Tasks;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Azure.Functions.Worker.Http;
using Microsoft.Extensions.Logging;
using System.Net;

public static class UploadPDF
{
    [Function("UploadPDF")]
    public static async Task<HttpResponseData> Run(
        [HttpTrigger(AuthorizationLevel.Function, "post", Route = null)] HttpRequestData req,
        FunctionContext executionContext)
    {
        var logger = executionContext.GetLogger("UploadPDF");
        logger.LogInformation("Procesando subida de PDF...");

        // Lee todo el body a memoria (NO recomendado para archivos grandes)
        using var ms = new MemoryStream();
        await req.Body.CopyToAsync(ms);
        var pdfBytes = ms.ToArray();

        // Aquí deberías procesar pdfBytes, guardarlos, analizarlos, etc.
        // Si quieres guardar el archivo en disco (solo para pruebas locales)
        var filePath = Path.Combine(Path.GetTempPath(), $"upload_{System.Guid.NewGuid()}.pdf");
        await File.WriteAllBytesAsync(filePath, pdfBytes);

        logger.LogInformation($"Archivo PDF guardado temporalmente en {filePath}");

        var response = req.CreateResponse(HttpStatusCode.OK);
        await response.WriteStringAsync($"Archivo PDF recibido ({pdfBytes.Length} bytes)");
        return response;
    }
}
