using Microsoft.Azure.Functions.Worker;
using Microsoft.Azure.Functions.Worker.Http;
using Microsoft.Extensions.Logging;
using Azure.Storage.Blobs;
using System.IO;
using System.Net;
using System.Threading.Tasks;

public class UploadCVFunction
{
    private readonly ILogger _logger;

    public UploadCVFunction(ILoggerFactory loggerFactory)
    {
        _logger = loggerFactory.CreateLogger<UploadCVFunction>();
    }

    [Function("UploadCV")]
    public async Task<HttpResponseData> Run(
        [HttpTrigger(AuthorizationLevel.Function, "post")] HttpRequestData req,
        FunctionContext executionContext)
    {
        _logger.LogInformation("UploadCVFunction triggered");

        var boundary = MultipartRequestHelper.GetBoundary(req.Headers.GetValues("Content-Type").First(), 4096);
        var reader = new MultipartReader(boundary, await req.BodyReader.AsStream().ConfigureAwait(false));
        var section = await reader.ReadNextSectionAsync();

        while (section != null)
        {
            var hasContentDispositionHeader = 
                ContentDispositionHeaderValue.TryParse(section.ContentDisposition, out var contentDisposition);

            if (hasContentDispositionHeader && contentDisposition.DispositionType.Equals("form-data") && 
                !string.IsNullOrEmpty(contentDisposition.FileName.Value))
            {
                var fileName = contentDisposition.FileName.Value;
                var stream = section.Body;

                // Aquí cambia tu connection string y container name
                string connectionString = Environment.GetEnvironmentVariable("AzureWebJobsStorage");
                var blobClient = new BlobContainerClient(connectionString, "cv-container");
                await blobClient.CreateIfNotExistsAsync();
                var blob = blobClient.GetBlobClient(fileName);
                await blob.UploadAsync(stream, overwrite: true);

                var response = req.CreateResponse(HttpStatusCode.OK);
                await response.WriteStringAsync("CV subido correctamente.");
                return response;
            }

            section = await reader.ReadNextSectionAsync();
        }

        var badResponse = req.CreateResponse(HttpStatusCode.BadRequest);
        await badResponse.WriteStringAsync("No se ha recibido un archivo válido.");
        return badResponse;
    }
}
