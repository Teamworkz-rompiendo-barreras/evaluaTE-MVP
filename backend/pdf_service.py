# backend/pdf_service.py
import os
import sys
import traceback
import asyncio
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from playwright.sync_api import sync_playwright
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def render_pdf_sync(html_content: str) -> bytes:
    """
    Función síncrona aislada (Thread Isolation).
    Evita colisiones con el Event Loop de Uvicorn/Windows al crear subprocesos.
    """
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
        except Exception as b_err:
            raise RuntimeError(f"Faltan binarios de Chromium: {b_err}")

        page = browser.new_page()
        page.set_content(html_content, wait_until="networkidle")
        
        pdf_bytes = page.pdf(
            format="A4",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            tagged=True  # OBLIGATORIO: Genera estructura semántica para WCAG
        )
        
        browser.close()
        return pdf_bytes

@router.post("/api/export-pdf")
async def export_pdf(request: Request):
    print("--- POST /api/export-pdf: Recibiendo petición del frontend ---", file=sys.stderr)
    
    try:
        try:
            body = await request.json()
        except Exception as json_err:
            print(f"CRÍTICO: Fallo al parsear el JSON: {json_err}", file=sys.stderr)
            raise HTTPException(status_code=400, detail="Payload corrupto")

        html_content = body.get("html_content")
        
        if not html_content:
            raise HTTPException(status_code=400, detail="No se proporcionó HTML")

        # Inyectamos el HTML del cliente en una plantilla optimizada
        full_html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Informe Profesional EvalúaTE</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <style>
                @media print {{
                    body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; background-color: white; }}
                    .break-inside-avoid {{ break-inside: avoid; page-break-inside: avoid; }}
                    .html2pdf__page-break {{ page-break-before: always; margin-top: 2rem; }}
                    button, form, .no-print {{ display: none !important; }}
                }}
            </style>
        </head>
        <body class="bg-white text-gray-900 font-sans">
            <main role="main" aria-label="Informe de Empleabilidad">
                {html_content}
            </main>
        </body>
        </html>
        """
        
        print("HTML procesado. Ejecutando Chromium en hilo síncrono aislado...", file=sys.stderr)
        
        # AISLAMIENTO DE HILO: Se delega a un Thread nativo, evadiendo el NotImplementedError
        pdf_bytes = await asyncio.to_thread(render_pdf_sync, full_html)
        
        print("✅ Exportación PDF completada con éxito.", file=sys.stderr)
        return Response(
            content=pdf_bytes, 
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=Informe_EvaluaTE.pdf"}
        )
                
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n[!] --- ERROR FATAL EN EXPORTACIÓN PDF --- [!]", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print(f"[!] ---------------------------------------- [!]\n", file=sys.stderr)
        
        raise HTTPException(status_code=500, detail=f"Fallo de renderizado: {str(e)}")