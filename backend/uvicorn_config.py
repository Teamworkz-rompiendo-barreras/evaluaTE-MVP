# backend/uvicorn_config.py
"""
Configuración de uvicorn con timeouts extendidos para evitar cancelaciones
de peticiones largas como la generación de informes.
"""

import uvicorn
from uvicorn.config import Config
from uvicorn.server import Server

def create_server_with_timeouts():
    """Crea un servidor uvicorn con timeouts extendidos"""
    
    config = Config(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        # Timeouts extendidos para evitar cancelaciones
        timeout_keep_alive=300,  # 5 minutos para keep-alive
        timeout_graceful_shutdown=300,  # 5 minutos para shutdown graceful
        # Configuraciones adicionales para estabilidad
        access_log=True,
        log_level="info",
        # Configuraciones para peticiones largas
        limit_concurrency=100,
        limit_max_requests=1000,
    )
    
    return Server(config=config)

if __name__ == "__main__":
    server = create_server_with_timeouts()
    server.run() 