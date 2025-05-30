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
    # Aquí iría tu lógica con OpenAI
    return f"Este es el informe para: {datos['nombre']} {datos['apellidos']} (aquí iría el informe real)"

# Para pruebas locales
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)