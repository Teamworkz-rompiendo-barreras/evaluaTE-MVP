#!/usr/bin/env python3
"""
Script para limpiar artifacts específicos de GitHub
"""

import os
import requests
import json
from datetime import datetime, timedelta

# Configuración
REPO_OWNER = "Teamworkz-rompiendo-barreras"
REPO_NAME = "evaluaTE-MVP"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Necesitas un token personal

def get_artifacts():
    """Obtener lista de artifacts"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/artifacts"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["artifacts"]
    else:
        print(f"Error obteniendo artifacts: {response.status_code}")
        return []

def delete_artifact(artifact_id):
    """Eliminar un artifact específico"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/artifacts/{artifact_id}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.delete(url, headers=headers)
    return response.status_code == 204

def cleanup_artifacts():
    """Limpiar artifacts antiguos"""
    artifacts = get_artifacts()
    
    if not artifacts:
        print("No se encontraron artifacts")
        return
    
    print(f"Encontrados {len(artifacts)} artifacts")
    
    # Calcular fecha límite (7 días atrás)
    cutoff_date = datetime.now() - timedelta(days=7)
    
    deleted_count = 0
    for artifact in artifacts:
        created_at = datetime.fromisoformat(artifact["created_at"].replace("Z", "+00:00"))
        
        # Eliminar artifacts antiguos o específicos
        if (created_at < cutoff_date or 
            artifact["name"] in ["frontend-build", "python-app"]):
            
            print(f"🗑️ Eliminando: {artifact['name']} (creado: {created_at.strftime('%Y-%m-%d %H:%M')})")
            
            if delete_artifact(artifact["id"]):
                deleted_count += 1
                print(f"✅ Eliminado: {artifact['name']}")
            else:
                print(f"❌ Error eliminando: {artifact['name']}")
    
    print(f"\n🎉 Eliminados {deleted_count} artifacts")

if __name__ == "__main__":
    if not GITHUB_TOKEN:
        print("❌ Error: GITHUB_TOKEN no configurado")
        print("Crea un token en: https://github.com/settings/tokens")
        print("Necesita permisos: repo, workflow")
    else:
        cleanup_artifacts()
