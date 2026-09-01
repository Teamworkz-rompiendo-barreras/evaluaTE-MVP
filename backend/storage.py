# backend/storage.py
import os
import logging
import boto3
from botocore.exceptions import ClientError

try:
    from backend.env_loader import load_backend_env
except ImportError:
    from env_loader import load_backend_env

load_backend_env()
logger = logging.getLogger(__name__)

# Configuración compatible con AWS S3 o MinIO
s3_client = boto3.client(
    's3',
    endpoint_url=os.getenv("MINIO_ENDPOINT", "http://127.0.0.1:9000"),
    aws_access_key_id=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
    aws_secret_access_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
    region_name="us-east-1"
)

BUCKET_NAME = "evaluate-cv-uploads"
_bucket_ready = False  # Bandera de inicialización perezosa (Lazy Init)

def _ensure_bucket_exists():
    """Se ejecuta solo cuando se necesita interactuar con S3, no al arrancar el servidor."""
    global _bucket_ready
    if _bucket_ready:
        return
        
    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        _bucket_ready = True
    except ClientError:
        try:
            s3_client.create_bucket(Bucket=BUCKET_NAME)
            _bucket_ready = True
            logger.info(f"Bucket '{BUCKET_NAME}' creado exitosamente en Object Storage.")
        except Exception as e:
            logger.error(f"Fallo crítico al crear bucket en S3/MinIO: {e}")
            raise
    except Exception as e:
        logger.error(f"El servidor de almacenamiento no está accesible: {e}")
        raise

def upload_pdf(file_bytes: bytes, file_key: str) -> str:
    """Sube el archivo binario al Object Storage."""
    _ensure_bucket_exists() # Comprobación de seguridad bajo demanda
    s3_client.put_object(Bucket=BUCKET_NAME, Key=file_key, Body=file_bytes, ContentType='application/pdf')
    return file_key

def download_pdf(file_key: str) -> bytes:
    """Descarga el archivo binario para el Worker."""
    _ensure_bucket_exists()
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_key)
    return response['Body'].read()

def delete_pdf(file_key: str):
    """Elimina el archivo por seguridad tras ser procesado."""
    _ensure_bucket_exists()
    s3_client.delete_object(Bucket=BUCKET_NAME, Key=file_key)