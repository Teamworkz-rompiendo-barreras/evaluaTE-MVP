# api/index.py
"""Entrypoint de Vercel Functions (Python). Vercel detecta la variable
`app` (ASGI) en este fichero y enruta aquí todo el tráfico de /api/*
(ver rewrites en vercel.json)."""
from backend.main import app
