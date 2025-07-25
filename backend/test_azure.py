import os
from openai import AzureOpenAI

# Configurar variables de entorno
os.environ["AZURE_OPENAI_API_KEY"] = "20cQLZWftwSfIdx1qyQGmiB2BQykDnmq2RSCz81MrOATK3eOFTseJQQJ99BEACYeBjFXJ3"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://teamworkz-openai.openai.azure.com/openai"
os.environ["AZURE_OPENAI_DEPLOYMENT"] = "gpt-4o"
os.environ["AZURE_OPENAI_API_VERSION"] = "2024-11-20"

# Crear cliente
client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"]
)

print("Variables de entorno:")
print(f"API_KEY: {os.environ['AZURE_OPENAI_API_KEY'][:10]}...")
print(f"ENDPOINT: {os.environ['AZURE_OPENAI_ENDPOINT']}")
print(f"DEPLOYMENT: {os.environ['AZURE_OPENAI_DEPLOYMENT']}")
print(f"API_VERSION: {os.environ['AZURE_OPENAI_API_VERSION']}")

try:
    # Prueba simple
    response = client.chat.completions.create(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        messages=[{"role": "user", "content": "Hola, ¿cómo estás?"}],
        max_tokens=50
    )
    print("✅ Éxito!")
    print(f"Respuesta: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Tipo de error: {type(e)}") 