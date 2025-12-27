import json
import adaptive_cards.card as ac
from typing import Any
from microsoft.teams.apps import ActivityContext
from microsoft.teams.api import MessageActivityInput

from enums import BotAction
from services.graph_service import GraphService
from services.email_service import EmailService
from services.openai_service import OpenAIService

def create_candidate_card_content(data: dict) -> dict:
    """Створює Adaptive Card для відображення кандидата"""
    full_name = f"{data.get('firstName')} {data.get('lastName')}"
    header = ac.ColumnSet(columns=[
        ac.Column(width="auto", items=[ac.Image(url="https://cdn-icons-png.flaticon.com/512/3135/3135715.png", size="Small", style="Person")]),
        ac.Column(width="stretch", items=[
            ac.TextBlock(text=full_name, weight="Bolder", size="Medium", wrap=True),
            ac.TextBlock(text=data.get('jobTitle', 'N/A'), is_subtle=True, spacing="None", wrap=True)
        ])
    ])
    details = ac.Container(style="emphasis", items=[
        ac.FactSet(facts=[
            ac.Fact(title="Email:", value=data.get('personalEmail') or "Not provided"),
            ac.Fact(title="Phone:", value=data.get('phoneNumber') or "Not provided"),
            ac.Fact(title="Location:", value=data.get('address') or "Not provided"),
        ])
    ])
    login_info = ac.Container(items=[
        ac.TextBlock(text="Proposed Login:", weight="Bolder", size="Small"),
        ac.TextBlock(text=f"{data.get('emailNickname')}@yourcompany.com", font_type="Monospace", color="Good", size="Medium")
    ])
    card = ac.AdaptiveCard(
        version="1.4",
        body=[ac.TextBlock(text="New Candidate Found", weight="Bolder", size="Medium", color="Accent"), header, details, login_info],
        actions=[
            ac.ActionSubmit(title="✅ Create User & Send Email", data={"action": "create_user", "candidate_data": data}),
            ac.ActionSubmit(title="❌ Reject", data={"action": "reject_candidate"})
        ]
    )
    return card.to_dict()

async def handle_action(ctx: ActivityContext, action: str, candidate_data: dict = None, 
                       graph_service: GraphService = None, email_service: EmailService = None):
    """Обробляє дії з картки кандидата"""
    if action == "create_user":
        if not candidate_data:
            await ctx.send("❌ Помилка: дані кандидата відсутні")
            return
        
        name = f"{candidate_data.get('firstName')} {candidate_data.get('lastName')}"
        personal_email = candidate_data.get('personalEmail')
        
        status_msg = await ctx.send(f"⚙️ Створюю акаунт для **{name}**...")
        
        # А. Створення в Azure AD
        ad_result = await graph_service.create_user(candidate_data)
        
        if ad_result["success"]:
            # Б. Відправка листа (якщо є email)
            email_status = "📭 Email кандидата не вказано, лист не надіслано."
            if personal_email:
                await ctx.send(f"📧 Відправляю доступи на `{personal_email}`...")
                
                print(f"🔄 Викликаю send_welcome_email для {personal_email}")
                email_result = await email_service.send_welcome_email(
                    to_email=personal_email,
                    candidate_name=name,
                    login=ad_result['email'],
                    password=ad_result['password']
                )
                
                print(f"📬 Результат відправки email: {email_result}")
                
                if email_result.get("success"):
                    email_status = f"✅ **Лист з доступами успішно надіслано кандидату на {personal_email}!**"
                    if email_result.get("id"):
                        email_status += f"\n📧 Message ID: {email_result['id']}"
                else:
                    error_msg = email_result.get('error', 'Невідома помилка')
                    email_status = f"❌ Помилка відправки листа: {error_msg}"
                    print(f"❌ Email не надіслано: {error_msg}")

            # В. Фінальний звіт
            license_status = ""
            if ad_result.get("license_assigned"):
                license_status = "\n📋 **Ліцензію успішно призначено**"
            elif ad_result.get("license_assigned") is False:
                license_error = ad_result.get("license_error")
                if license_error:
                    license_status = f"\n⚠️ **Ліцензію не вдалося призначити:** {license_error}"
                else:
                    license_status = "\n⚠️ **Ліцензію не вдалося призначити** (перевірте налаштування DEFAULT_LICENSE_SKU_ID)"
            
            msg = (
                f"🎉 **Користувача успішно створено!**\n\n"
                f"👤 **Login:** `{ad_result['email']}`\n"
                f"🔑 **Password:** `{ad_result['password']}`"
                f"{license_status}\n\n"
                f"{email_status}"
            )
            await ctx.send(msg)
        else:
            await ctx.send(f"❌ Помилка Azure AD: {ad_result['error']}")

    elif action == BotAction.REJECT_CANDIDATE.value:
        await ctx.send("🗑️ Кандидата відхилено.")

async def run_flow(ctx: ActivityContext, intent_data: dict, 
                  openai_service: OpenAIService, 
                  graph_service: GraphService, 
                  email_service: EmailService):
    """Головний flow онбордингу: парсинг резюме -> картка кандидата"""
    
    # Перевіряємо, чи це дія з картки
    if ctx.activity.value and "action" in ctx.activity.value:
        action = ctx.activity.value["action"]
        candidate_data = ctx.activity.value.get("candidate_data")
        await handle_action(ctx, action, candidate_data, graph_service, email_service)
        return
    
    # Перевіряємо, чи дані кандидата вже розпарсені (з app.py)
    parsed_data = intent_data.get("candidate_data")
    
    # Якщо немає - парсимо з повідомлення
    if not parsed_data:
        user_text = ctx.activity.text
        parsed_data = await openai_service.parse_candidate_data(user_text)
    
    if "error" in parsed_data:
        await ctx.send("⚠️ Не бачу даних кандидата. Будь ласка, надайте інформацію про кандидата (ім'я, прізвище, посада тощо).")
    else:
        # Створюємо та відправляємо картку
        card = create_candidate_card_content(parsed_data)
        await ctx.send(MessageActivityInput(
            type="message", 
            attachments=[{
                "contentType": "application/vnd.microsoft.card.adaptive", 
                "content": card
            }]
        ))

