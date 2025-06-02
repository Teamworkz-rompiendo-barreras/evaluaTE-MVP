using System.IO;
using System.Threading.Tasks;
using System.Net;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Azure.Functions.Worker.Http;
using Microsoft.Extensions.Logging;
using System.Text.Json;

public static class GenerarInformeFunction
{
    [Function("GenerarInforme")]
    public static async Task<HttpResponseData> Run(
        [HttpTrigger(AuthorizationLevel.Function, "post", Route = "generar-informe")] HttpRequestData req,
        FunctionContext executionContext)
    {
        var logger = executionContext.GetLogger("GenerarInforme");
        logger.LogInformation("Generando informe...");

        // Lee el cuerpo del request (los datos enviados por el frontend)
        string body = await new StreamReader(req.Body).ReadToEndAsync();

        // Si quieres, puedes deserializar aquí el JSON recibido, ejemplo:
        // var datos = JsonSerializer.Deserialize<DatosFormulario>(body);

        // Respuesta simulada de prueba (pon aquí los campos que usa tu frontend)
        var resultado = new
        {
            nombre = "Ejemplo",
            apellidos = "Apellidos",
            email = "ejemplo@email.com",
            whatsapp = "123456789",
            resumen = "Este es un resumen simulado de tu perfil.",
            fortalezas = new[] { "Trabajo en equipo", "Comunicación" },
            areas_mejora = new[] { "Gestión del tiempo" },
            orientacion = "Prueba de orientación laboral personalizada.",
            conclusion = "Esto es una conclusión de ejemplo."
        };

        var response = req.CreateResponse(HttpStatusCode.OK);
        response.Headers.Add("Content-Type", "application/json");
        await response.WriteStringAsync(JsonSerializer.Serialize(resultado));
        return response;
    }
}
