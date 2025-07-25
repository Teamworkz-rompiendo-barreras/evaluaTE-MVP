import os
from openai import AzureOpenAI

# Configurar variables de entorno
os.environ["AZURE_OPENAI_API_KEY"] = "20cQLZWftwSfIdx1qyQGmiB2BQykDnmq2RSCz81MrOATK3eOFTseJQQJ99BEACYeBjFXJ3"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://teamworkz-openai.openai.azure.com/"  # Endpoint base
os.environ["AZURE_OPENAI_DEPLOYMENT"] = "gpt-4o-backend"  # Nuevo deployment
os.environ["AZURE_OPENAI_API_VERSION"] = "2024-11-20"

# Crear cliente
client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"]
)

print("=== VERIFICACIÓN DE REGIONES ===")
print(f"Backend - Endpoint: {os.environ['AZURE_OPENAI_ENDPOINT']}")
print(f"Backend - Deployment: {os.environ['AZURE_OPENAI_DEPLOYMENT']}")
print(f"Backend - Región esperada: East US")
print(f"Frontend - URL: http://localhost:3006/")
print(f"Frontend - Puerto: 3006")
print()

try:
    # Prueba simple
    response = client.chat.completions.create(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        messages=[{"role": "user", "content": "Hola, ¿cómo estás?"}],
        max_tokens=50
    )
    print("✅ Éxito! Azure OpenAI funciona correctamente")
    print(f"Respuesta: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Tipo de error: {type(e)}")
    
    print(f"\n=== DIAGNÓSTICO ===")
    print(f"1. Verificar que el deployment 'gpt-4o-backend' existe en Azure AI Studio")
    print(f"2. Verificar que la región del deployment es 'East US'")
    print(f"3. Verificar que no hay restricciones de red en el recurso")
    print(f"4. Verificar que el endpoint es correcto para la región East US") 