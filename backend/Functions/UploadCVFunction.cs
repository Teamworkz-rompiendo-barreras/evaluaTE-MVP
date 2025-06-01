using System.IO;
using System.Linq; 
using System.Threading.Tasks;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Azure.Functions.Worker.Http;
using Microsoft.Extensions.Logging;

public class UploadCVFunction
{
    private readonly ILogger _logger;

    public UploadCVFunction(ILoggerFactory loggerFactory)
    {
        _logger = loggerFactory.CreateLogger<UploadCVFunction>();
    }

    [Function("UploadCV")]
    public async Task<HttpResponseData> Run(
        [HttpTrigger(AuthorizationLevel.Function, "post")] HttpRequestData req)
    {
        _logger.LogInformation("Procesando la subida de un CV...");

        // Asegúrate de que el content-type sea multipart/form-data
        var contentType = req.Headers.GetValues("content-type").FirstOrDefault();
        if (string.IsNullOrEmpty(contentType) || !contentType.Contains("multipart/form-data"))
        {
            var badResponse = req.CreateResponse(HttpStatusCode.BadRequest);
            await badResponse.WriteStringAsync("Content-Type debe ser multipart/form-data");
            return badResponse;
        }

        // Parsear el body como multipart
        var parser = await MultipartFormDataParser.ParseAsync(req.Body);
        var file = parser.Files.FirstOrDefault();

        if (file == null)
        {
            var badResponse = req.CreateResponse(HttpStatusCode.BadRequest);
            await badResponse.WriteStringAsync("No se ha adjuntado ningún archivo PDF.");
            return badResponse;
        }

        // Guardar el archivo (por ejemplo en disco temporal)
        var filePath = Path.Combine(Path.GetTempPath(), file.FileName);
        using (var fileStream = File.Create(filePath))
        {
            await file.Data.CopyToAsync(fileStream);
        }

        _logger.LogInformation($"Archivo {file.FileName} guardado correctamente en {filePath}");

        var response = req.CreateResponse(HttpStatusCode.OK);
        await response.WriteStringAsync($"Archivo {file.FileName} recibido correctamente.");
        return response;
    }
}
