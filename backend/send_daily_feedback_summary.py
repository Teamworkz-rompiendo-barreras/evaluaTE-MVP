#!/usr/bin/env python3
"""
Script para enviar resumen diario de feedback de la IA.
Se puede ejecutar manualmente o configurar como tarea programada (cron job).
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from feedback_notifications import feedback_notifier
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('feedback_summary.log'),
        logging.StreamHandler()
    ]
)

def main():
    """Función principal para enviar el resumen diario"""
    try:
        logging.info("🔄 Iniciando envío de resumen diario de feedback...")
        
        # Enviar resumen diario
        success = feedback_notifier.send_daily_summary()
        
        if success:
            logging.info("✅ Resumen diario enviado correctamente")
        else:
            logging.info("ℹ️ No hay feedback del día para enviar")
            
    except Exception as e:
        logging.error(f"❌ Error enviando resumen diario: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()