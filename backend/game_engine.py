# backend/game_engine.py

# El mapa de puntuaciones nunca se expone a React. 
# Evitamos que el candidato modifique su puntuación en local.
GAME_SCORES = {
    "decision-making": {
        "soft_skill": "Toma de decisiones",
        "scenes": {
            "prueba-1": {"archivar": 50, "ayudar": 100, "revisar": 20},
            "prueba-2": {"reunion": 20, "tarea": 100, "ayuda": 50},
            "prueba-3": {"compañero": 20, "esperar": 50, "atender": 100},
            "prueba-4": {"solucionar": 100, "mantenimiento": 50, "otra": 20},
            "prueba-5": {"opinion": 100, "no-opinar": 20, "preguntar": 50}
        }
    }
    # (Se completaría con los 9 juegos restantes)
}

def evaluate_decision(game_id: str, scene_id: str, option_id: str) -> int:
    """Retorna el peso de la decisión. Retorna 0 si hay intento de fraude."""
    try:
        return GAME_SCORES[game_id]["scenes"][scene_id][option_id]
    except KeyError:
        return 0