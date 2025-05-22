using Microsoft.Azure.Functions.Worker;
using Microsoft.Azure.Functions.Worker.Http;
using Microsoft.Extensions.Logging;
using System.IO;
using System.Net;
using System.Threading.Tasks;

public class UploadCV
{
    private readonly ILogger _logger;

    public UploadCV(ILoggerFactory loggerFactory)
    {
        _logger = loggerFactory.CreateLogger<UploadCV>();
    }

    [Function("UploadCV")]
    public async Task<HttpResponseData> Run([HttpTrigger(AuthorizationLevel.Function, "post", Route = null)] HttpRequestData req)
    {
        var response = req.CreateResponse(HttpStatusCode.OK);
        var reader = new StreamReader(req.Body);
        var text = await reader.ReadToEndAsync();

        await response.WriteStringAsync($"CV recibido. Texto simulado: {text.Substring(0, System.Math.Min(100, text.Length))}...");
        return response;
    }
}
