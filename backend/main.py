from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Habilita CORS para tu frontend (localhost, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto a tu dominio en producción
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/generar-informe")
async def generar_informe_endpoint(request: Request):
    datos = await request.json()  # Recibe JSON del frontend
    # Aquí llamas a tu función con IA, por ahora sólo simulamos:
    informe = generar_informe(datos)  # Esta función ya la tienes hecha
    return {"informe": informe}

def generar_informe(datos):
    # Estructura compatible con el frontend
    return {
        "nombre": datos.get("nombre", ""),
        "apellidos": datos.get("apellidos", ""),
        "email": datos.get("email", ""),
        "whatsapp": datos.get("whatsapp", ""),
        "resumen": f"Este es un informe de ejemplo para {datos.get('nombre', '')}. Aquí irá el resumen real.",
        "fortalezas": ["Comunicación", "Resolución de problemas"],
        "areas_mejora": ["Gestión del tiempo"],
        "orientacion": "Se recomienda buscar trabajos en equipo de atención al público.",
        "conclusion": "¡Enhorabuena por tus avances!"
    }

# Para pruebas locales
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)