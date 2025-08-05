# backend/production.py
"""
Configuración específica para producción
"""

import os
from typing import List

# Configuración de seguridad
SECURITY_CONFIG = {
    "ALLOWED_HOSTS": [
        "yellow-mud-0b6281c1e.6.azurestaticapps.net",
        "*.azurestaticapps.net",
        "*.azurewebsites.net"
    ],
    "CORS_ORIGINS": [
        "https://yellow-mud-0b6281c1e.6.azurestaticapps.net",
        "https://*.azurestaticapps.net",
        "https://*.azurewebsites.net"
    ],
    "MAX_FILE_SIZE": 10 * 1024 * 1024,  # 10MB
    "RATE_LIMIT": {
        "requests_per_minute": 60,
        "burst_size": 10
    }
}

# Configuración de logging
LOGGING_CONFIG = {
    "level": "WARNING",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": ["console", "file"],
    "file_handler": {
        "filename": "logs/app.log",
        "max_bytes": 10 * 1024 * 1024,  # 10MB
        "backup_count": 5
    }
}

# Configuración de Azure
AZURE_CONFIG = {
    "TIMEOUT": 300,  # 5 minutos
    "RETRY_ATTEMPTS": 3,
    "RETRY_DELAY": 1,  # segundos
}

# Configuración de limpieza
CLEANUP_CONFIG = {
    "TEMP_FILE_RETENTION": 3600,  # 1 hora
    "LOG_RETENTION_DAYS": 30,
    "MAX_CONCURRENT_REQUESTS": 10
}

def get_production_settings():
    """Obtiene la configuración de producción"""
    return {
        "security": SECURITY_CONFIG,
        "logging": LOGGING_CONFIG,
        "azure": AZURE_CONFIG,
        "cleanup": CLEANUP_CONFIG,
        "debug": False,
        "reload": False,
        "workers": 1
    }

def validate_production_environment():
    """Valida que el entorno esté configurado para producción"""
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_DEPLOYMENT",
        "AZURE_OPENAI_API_VERSION"
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        raise ValueError(f"Variables de entorno faltantes para producción: {', '.join(missing)}")
    
    return True 