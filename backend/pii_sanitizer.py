# backend/pii_sanitizer.py
# -*- coding: utf-8 -*-
import re
import logging

logger = logging.getLogger(__name__)

class RegexPIISanitizer:
    def __init__(self):
        # Expresiones regulares robustas enfocadas al marco legal europeo y español
        self.email_regex = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
        self.phone_regex = re.compile(r"(\+?\d{1,3}[\s-]?)?\(?\d{2,3}\)?[\s.-]?\d{3}[\s.-]?\d{3,4}")
        self.dni_regex = re.compile(r"\b\d{8}[A-Z]\b", re.IGNORECASE)
        self.nie_regex = re.compile(r"\b[XYZ]\d{7}[A-Z]\b", re.IGNORECASE)
        self.ssn_regex = re.compile(r"\b\d{11,12}\b") # Números de Seguridad Social genéricos
        self.iban_regex = re.compile(r"\b[A-Z]{2}\d{2}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{2,4}\b")
        
    def anonymize_text(self, text: str) -> str:
        """
        Escanea el texto y sustituye los identificadores personales por etiquetas seguras
        antes de enviarlos a servicios de IA de terceros.
        """
        if not text:
            return ""
        
        try:
            # Reemplazo secuencial de vulnerabilidades
            sanitized = self.email_regex.sub("[EMAIL_PROTEGIDO]", text)
            sanitized = self.phone_regex.sub("[TELEFONO_PROTEGIDO]", sanitized)
            sanitized = self.dni_regex.sub("[DNI_PROTEGIDO]", sanitized)
            sanitized = self.nie_regex.sub("[NIE_PROTEGIDO]", sanitized)
            sanitized = self.ssn_regex.sub("[SS_PROTEGIDO]", sanitized)
            sanitized = self.iban_regex.sub("[CUENTA_BANCARIA_PROTEGIDA]", sanitized)
            
            return sanitized
        except Exception as e:
            logger.error(f"Fallo crítico en el motor Regex de sanitización: {e}")
            return text 

# Instancia global (Singleton) para ser consumida por main.py y cv_analyzer.py sin instanciar repetidas veces
sanitizer = RegexPIISanitizer()