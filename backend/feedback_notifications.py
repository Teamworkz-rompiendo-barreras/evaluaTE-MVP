import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
from dotenv import load_dotenv

load_dotenv()

class FeedbackNotifier:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_user = os.getenv("EMAIL_USER")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.admin_email = os.getenv("ADMIN_EMAIL")
        
    def send_feedback_notification(self, feedback_data):
        """
        Envía una notificación por email cuando se recibe nuevo feedback
        """
        if not all([self.email_user, self.email_password, self.admin_email]):
            print("⚠️ Configuración de email incompleta. No se enviarán notificaciones.")
            return False
            
        try:
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = self.admin_email
            msg['Subject'] = f"🆕 Nuevo Feedback IA - {feedback_data['rating']}"
            
            # Crear contenido del email
            body = self._create_email_body(feedback_data)
            msg.attach(MIMEText(body, 'html'))
            
            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
                
            print(f"✅ Notificación de feedback enviada a {self.admin_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error enviando notificación: {str(e)}")
            return False
    
    def send_daily_summary(self):
        """
        Envía un resumen diario de feedback
        """
        try:
            feedback_file = "feedback_ia.json"
            if not os.path.exists(feedback_file):
                return False
                
            with open(feedback_file, 'r', encoding='utf-8') as f:
                feedbacks = json.load(f)
            
            # Filtrar feedbacks de hoy
            today = datetime.now().date()
            today_feedbacks = [
                f for f in feedbacks 
                if datetime.fromisoformat(f['timestamp']).date() == today
            ]
            
            if not today_feedbacks:
                return False
            
            # Crear resumen
            useful_count = len([f for f in today_feedbacks if f['rating'] == 'Útil'])
            not_useful_count = len([f for f in today_feedbacks if f['rating'] == 'No útil'])
            
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = self.admin_email
            msg['Subject'] = f"📊 Resumen Diario Feedback IA - {today.strftime('%d/%m/%Y')}"
            
            body = self._create_daily_summary_body(today_feedbacks, useful_count, not_useful_count)
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
                
            print(f"✅ Resumen diario enviado a {self.admin_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error enviando resumen diario: {str(e)}")
            return False
    
    def _create_email_body(self, feedback_data):
        """Crea el contenido HTML del email de notificación"""
        rating_icon = "👍" if feedback_data['rating'] == 'Útil' else "👎"
        rating_color = "green" if feedback_data['rating'] == 'Útil' else "red"
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
                <h2 style="color: #333;">🆕 Nuevo Feedback Recibido</h2>
                
                <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <div style="display: flex; align-items: center; margin-bottom: 15px;">
                        <span style="font-size: 24px; margin-right: 10px;">{rating_icon}</span>
                        <span style="color: {rating_color}; font-weight: bold; font-size: 18px;">
                            {feedback_data['rating']}
                        </span>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <strong>Comentario:</strong><br>
                        <p style="background-color: #f8f9fa; padding: 10px; border-radius: 4px; margin: 5px 0;">
                            {feedback_data.get('comment', 'Sin comentarios')}
                        </p>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <strong>Fecha:</strong> {datetime.fromisoformat(feedback_data['timestamp']).strftime('%d/%m/%Y %H:%M')}
                    </div>
                    
                    {self._format_user_data(feedback_data.get('userData', {}))}
                </div>
                
                <div style="text-align: center; margin-top: 20px;">
                    <a href="http://localhost:3000/feedback-dashboard" 
                       style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">
                        Ver Dashboard
                    </a>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_daily_summary_body(self, feedbacks, useful_count, not_useful_count):
        """Crea el contenido HTML del resumen diario"""
        total = len(feedbacks)
        satisfaction_rate = (useful_count / total * 100) if total > 0 else 0
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
                <h2 style="color: #333;">📊 Resumen Diario - Feedback IA</h2>
                
                <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                        <div style="text-align: center; padding: 15px; background-color: #e3f2fd; border-radius: 4px;">
                            <div style="font-size: 24px; font-weight: bold; color: #1976d2;">{total}</div>
                            <div style="font-size: 14px; color: #666;">Total</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background-color: #e8f5e8; border-radius: 4px;">
                            <div style="font-size: 24px; font-weight: bold; color: #2e7d32;">{useful_count}</div>
                            <div style="font-size: 14px; color: #666;">Útil</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background-color: #ffebee; border-radius: 4px;">
                            <div style="font-size: 24px; font-weight: bold; color: #c62828;">{not_useful_count}</div>
                            <div style="font-size: 14px; color: #666;">No Útil</div>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-bottom: 20px;">
                        <div style="font-size: 18px; font-weight: bold; color: #333;">
                            Satisfacción: {satisfaction_rate:.1f}%
                        </div>
                    </div>
                    
                    <h3 style="color: #333; margin-bottom: 10px;">Comentarios del día:</h3>
                    {self._format_daily_comments(feedbacks)}
                </div>
                
                <div style="text-align: center; margin-top: 20px;">
                    <a href="http://localhost:3000/feedback-dashboard" 
                       style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">
                        Ver Dashboard Completo
                    </a>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _format_user_data(self, user_data):
        """Formatea los datos del usuario para el email"""
        if not user_data:
            return ""
        
        minigames_count = len(user_data.get('minigames', []))
        preferences = user_data.get('preferences', {})
        areas = preferences.get('areas', [])
        
        return f"""
        <div style="margin-bottom: 15px;">
            <strong>Datos del Usuario:</strong><br>
            <ul style="margin: 5px 0; padding-left: 20px;">
                <li>Habilidades evaluadas: {minigames_count}</li>
                {f'<li>Áreas de interés: {", ".join(areas)}</li>' if areas else ''}
            </ul>
        </div>
        """
    
    def _format_daily_comments(self, feedbacks):
        """Formatea los comentarios del día"""
        if not feedbacks:
            return "<p style='color: #666; font-style: italic;'>No hay comentarios para mostrar.</p>"
        
        comments_html = ""
        for i, feedback in enumerate(feedbacks[:5], 1):  # Solo mostrar los primeros 5
            rating_icon = "👍" if feedback['rating'] == 'Útil' else "👎"
            comment = feedback.get('comment', 'Sin comentarios')
            time = datetime.fromisoformat(feedback['timestamp']).strftime('%H:%M')
            
            comments_html += f"""
            <div style="border-left: 3px solid #007bff; padding-left: 10px; margin-bottom: 10px;">
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <span style="margin-right: 5px;">{rating_icon}</span>
                    <span style="font-size: 12px; color: #666;">{time}</span>
                </div>
                <p style="margin: 0; color: #333;">{comment}</p>
            </div>
            """
        
        if len(feedbacks) > 5:
            comments_html += f"<p style='color: #666; font-size: 12px;'>... y {len(feedbacks) - 5} más</p>"
        
        return comments_html

# Instancia global del notificador
feedback_notifier = FeedbackNotifier()