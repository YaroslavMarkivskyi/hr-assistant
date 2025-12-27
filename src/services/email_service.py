from azure.communication.email.aio import EmailClient
from typing import Dict, Any

class EmailService:
    def __init__(self, config):
        self.connection_string = config.COMMUNICATION_CONNECTION_STRING
        self.sender_address = config.MAIL_FROM_ADDRESS

    async def send_welcome_email(self, to_email: str, candidate_name: str, login: str, password: str) -> Dict[str, Any]:
        """Відправляє вітальний лист з доступами"""
        
        # Перевірка налаштувань
        if not self.connection_string:
            error_msg = "COMMUNICATION_CONNECTION_STRING не налаштовано"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
        
        if not self.sender_address:
            error_msg = "MAIL_FROM_ADDRESS не налаштовано"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
        
        if not to_email:
            error_msg = "Email отримувача не вказано"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

        print(f"📧 Підготовка листа для: {to_email} (від: {self.sender_address})")

        # HTML шаблон листа
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="background-color: #f4f4f4; padding: 20px;">
                    <div style="background-color: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: auto;">
                        <h2 style="color: #0078D4;">Welcome to the Team, {candidate_name}! 🚀</h2>
                        <p>We are excited to have you on board. Here are your corporate credentials to get started:</p>
                        
                        <div style="background-color: #f0f0f0; padding: 15px; border-left: 5px solid #0078D4; margin: 20px 0;">
                            <p><strong>📧 Login:</strong> {login}</p>
                            <p><strong>🔑 Password:</strong> {password}</p>
                        </div>

                        <p>Please log in at <a href="https://portal.office.com">portal.office.com</a> and change your password immediately.</p>
                        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="font-size: 12px; color: #888;">Best regards,<br>IT Support Team</p>
                    </div>
                </div>
            </body>
        </html>
        """

        message = {
            "content": {
                "subject": "Your Corporate Account Details 🔐",
                "plainText": f"Welcome! Login: {login}, Password: {password}",
                "html": html_content
            },
            "recipients": {
                "to": [{"address": to_email, "displayName": candidate_name}]
            },
            "senderAddress": self.sender_address
        }

        try:
            print(f"⏳ Ініціалізація EmailClient з connection string...")
            # Ініціалізуємо клієнт асинхронно
            client = EmailClient.from_connection_string(self.connection_string)
            
            async with client:
                print(f"⏳ Відправка листа в Azure Communication Services...")
                print(f"   To: {to_email}")
                print(f"   From: {self.sender_address}")
                
                # Починаємо відправку (повертає poller)
                poller = await client.begin_send(message)
                print(f"✅ Запит на відправку прийнято, очікуємо результат...")
                
                # Чекаємо завершення відправки
                # poller.result() чекає поки операція завершиться
                result = await poller.result()
            
            # --- ДІАГНОСТИКА ---
            print(f"📧 EMAIL RESULT RAW: {result}")
            print(f"📧 EMAIL RESULT TYPE: {type(result)}")
            
            # --- БЕЗПЕЧНЕ ОТРИМАННЯ ID ---
            # Azure Communication Services Email може повертати різні формати
            if isinstance(result, dict):
                msg_id = result.get('id') or result.get('messageId') or result.get('message_id') or "Unknown ID"
            elif hasattr(result, 'id'):
                msg_id = result.id
            elif hasattr(result, 'message_id'):
                msg_id = result.message_id
            else:
                msg_id = str(result) if result else "Unknown ID"
            
            print(f"✅ Лист успішно надіслано! Message ID: {msg_id}")
            return {"success": True, "id": msg_id}
            
        except Exception as e:
            # Виведемо повний текст помилки в консоль для ясності
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ EMAIL ERROR: {str(e)}")
            print(f"❌ TRACEBACK:\n{error_details}")
            return {"success": False, "error": str(e)}

