using Microsoft.Azure.Functions.Worker;
using Microsoft.Azure.Functions.Worker.Http;
using Microsoft.Extensions.Logging;
using System.Net;
using System.Threading.Tasks;

namespace TuNamespace // Cambia por el tuyo si quieres
{
    public class UploadCV
    {
        private readonly ILogger<UploadCV> _logger;

        public UploadCV(ILoggerFactory loggerFactory)
        {
            _logger = loggerFactory.CreateLogger<UploadCV>();
        }

        [Function("UploadCV")]
        public async Task<HttpResponseData> Run(
            [HttpTrigger(AuthorizationLevel.Function, "post")] HttpRequestData req)
        {
            _logger.LogInformation("Procesando subida de CV");

            // Lee el cuerpo directamente como string
            string body = await req.ReadAsStringAsync();

            var response = req.CreateResponse(HttpStatusCode.OK);
            await response.WriteStringAsync($"CV recibido. Texto simulado: {(body.Length > 100 ? body.Substring(0, 100) + "..." : body)}");

            return response;
        }
    }
}
