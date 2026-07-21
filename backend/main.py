# backend/main.py
# -*- coding: utf-8 -*-
import os
import json
import logging
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, Depends, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel

from database import get_db, engine, Base
from database_models import EmployabilityReport, User
from cv_analyzer import extract_and_anonymize_cv, analyze_multimodal_report
from new_report_schema import NewReportSchema
from pii_sanitizer import sanitizer

logger = logging.getLogger("teamworkz_backend")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Teamworkz Core API (MVP Privado)", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite conexiones desde el puerto 3005 del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GuestUser:
    id = "guest_mvp_001"
    first_name = "Candidato"
    email = "anonimo@teamworkz.com"

class FeedbackModel(BaseModel):
    informe: Optional[str] = ""
    rating: str
    comment: Optional[str] = ""

def _ensure_guest_user(db: Session, guest_id: str):
    try:
        sql = text("INSERT IGNORE INTO users (id, first_name, email) VALUES (:id, 'Candidato', 'anonimo@teamworkz.com')")
        db.execute(sql, {"id": guest_id})
        db.commit()
    except Exception as e:
        db.rollback()
        logger.warning(f"Aviso BD: {e}")

def _db_insert_report(user_id: str, score: int, level: str, report_json: dict, db: Session):
    try:
        _ensure_guest_user(db, user_id)
        new_report = EmployabilityReport(
            user_id=user_id, employability_score=score, level=level, report_json=report_json
        )
        db.add(new_report)
        db.commit()
    except Exception as e:
        logger.error(f"Error guardando reporte en BD: {e}")
        db.rollback()

@app.post("/api/pdf/analyze-cv", response_model=NewReportSchema)
@app.post("/api/analyze", response_model=NewReportSchema)
async def analyze_computational_profile(
    background_tasks: BackgroundTasks,
    cv_file: Optional[UploadFile] = File(None),
    game_results: str = Form("{}"),
    preferences: str = Form("{}"),
    db: Session = Depends(get_db)
):
    current_user = GuestUser()
    try:
        games_data = json.loads(game_results)
        prefs_data = json.loads(preferences)
        real_name = prefs_data.get("fullName") or "Usuario"
        
        cv_text_raw = ""
        if cv_file:
            cv_text_raw = await extract_and_anonymize_cv(cv_file)
            
        if not cv_text_raw or not cv_text_raw.strip():
            cv_text_raw = "El candidato no aportó CV o el documento estaba vacío."
            
        cv_text_safe = sanitizer.anonymize_text(cv_text_raw)
        skills_str = json.dumps(games_data.get("softSkills", []), ensure_ascii=False)
        prefs_str = json.dumps(prefs_data, ensure_ascii=False)

        # FIX IA: Regla estricta de viabilidad física y técnica
        prompt = f"""
        Eres un Orientador Laboral Senior, Headhunter y Consultor de Talento de la plataforma Teamworkz.
        Tu objetivo es redactar un 'Informe Profesional de Empleabilidad' de nivel consultoría premium.

        DATOS DEL CANDIDATO PARA ANALIZAR:
        Preferencias Laborales y Rol Objetivo: {prefs_str}
        Resultados de Minijuegos (Soft Skills): {skills_str}
        Texto extraído de su CV:
        <CV_TEXT>
        {cv_text_safe}
        </CV_TEXT>

        REGLAS DE AUDITORÍA CRÍTICA (ANTI-ALUCINACIONES Y REALISMO FÍSICO ABSOLUTO):
        1. IMPOSIBILIDAD FÍSICA O LEGAL: Si el candidato solicita una combinación absurda de profesión y modalidad (ej. 'Aviador en remoto', 'Jardinero teletrabajando', 'Cirujano a distancia'), DEBES DENUNCIARLO EXPLÍCITAMENTE en el 'resumen_ejecutivo' y la 'interpretacion_global' indicando que es físicamente irrealizable.
        2. PENALIZACIÓN DE PUNTAJE: En caso de pedir un absurdo físico o carecer del 100% de la formación obligatoria, la 'puntuacion_global' NO PUEDE superar los 60 puntos.
        3. REORIENTACIÓN OBLIGATORIA: Si su deseo es imposible, los 'roles_recomendados' y el 'plan_accion' deben ignorar su fantasía y ofrecer alternativas 100% realistas basadas en sus soft skills, o la formación puente requerida.
        4. OBLIGATORIO: Personaliza dirigiéndote a {real_name}. USA ASTERISCOS DOBLES (**texto**) para enfatizar lo más importante.

        DEVUELVE ÚNICAMENTE UN OBJETO JSON VÁLIDO CON ESTA ESTRUCTURA EXACTA (14 PUNTOS SECUENCIALES):
        {{
          "datos_personales": {{"nombre": "{real_name}", "ciudad": "Extraer", "disponibilidad": "Extraer", "modalidad": "Extraer"}},
          "resumen_ejecutivo": "Análisis premium detallado. Si su preferencia es físicamente irrealizable en remoto, indícalo aquí de forma firme y constructiva.",
          "puntuacion_global": 85,
          "interpretacion_global": "Explicación de la puntuación. Justifica si se penaliza por pedir un absurdo físico o falta de formación vital.",
          "perfil_competencias": [
            {{"categoria": "Competencias cognitivas", "competencias": [{{"nombre": "Toma de decisiones", "puntuacion": 100, "nivel": "Alto", "explicacion": "..."}}]}}
          ],
          "fortalezas_principales": [{{"nombre": "Nombre de fortaleza", "explicacion_practica": "..."}}],
          "areas_mejora": [{{"nombre": "Brecha de capacitación o realismo", "porque_afecta": "Explicar la limitación", "como_mejorar": "Plan de corrección", "acciones_concretas": ["Acción 1..."]}}],
          "analisis_cv": {{
            "resumen": "Auditoría...",
            "experiencia": ["..."], "formacion": ["..."], "idiomas": ["..."], "software": ["..."],
            "valoraciones": {{"formato": 4, "claridad": 4, "coherencia": 3, "info_clave": 4, "ortografia": 5}},
            "puntos_fuertes": ["..."], "aspectos_mejorar": ["..."],
            "ats_compatibilidad": 40,
            "ats_explicacion": "Análisis ATS."
          }},
          "entornos_ideales": ["Ambientes donde destaca..."],
          "roles_recomendados": [{{"titulo": "Alternativa Realista o Transición", "nivel": "Junior", "modalidad": "Presencial/Remoto", "por_que_encaja": "Justificación de encaje lógico", "salario_orientativo": "20k", "demanda_laboral": "Alta"}}],
          "plan_accion": {{"dias_30": ["Formación inicial en..."], "dias_60": ["Prácticas en..."], "dias_90": ["Postulación a..."]}},
          "estrategia_busqueda": ["Estrategia de posicionamiento..."],
          "herramientas_recomendadas": [{{"nombre": "Herramienta", "para_que_sirve": "..."}}],
          "resultados_juegos": [{{"juego": "Nombre", "que_mide": "...", "resultado": "...", "interpretacion": "...", "aplicacion_entrevista": "..."}}],
          "recomendaciones_personalizadas": ["Consejo directivo enfocado en su realidad..."],
          "recursos_adicionales": [{{"nombre": "Curso o titulación exacta", "tipo": "Formación Habilitante", "descripcion": "Explicación de por qué es indispensable."}}],
          "mensaje_final": "Conclusión de reorientación y empoderamiento..."
        }}
        """

        report_data = await analyze_multimodal_report(prompt)
        
        if not report_data.get("success"):
            raise HTTPException(status_code=503, detail="El motor de análisis está temporalmente saturado.")

        final_report = report_data["data"]

        background_tasks.add_task(
            _db_insert_report, current_user.id, final_report.get("puntuacion_global", 0), "medio", final_report, db
        )

        return final_report

    except HTTPException as http_exc:
        raise http_exc
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as e:
        logger.exception("Fallo crítico en el enrutador de análisis")
        raise HTTPException(status_code=500, detail="Error estructurando la evaluación.")

@app.get("/api/auth/me")
async def get_current_user_info():
    return {"id": "guest_mvp_001", "first_name": "Candidato", "email": "anonimo@teamworkz.com"}

@app.post("/api/informe-ia/feedback")
async def receive_feedback(feedback: FeedbackModel):
    logger.info(f"Feedback Registrado -> Rating: {feedback.rating} | Comentario: {feedback.comment}")
    return {"success": True, "message": "Feedback almacenado correctamente."}