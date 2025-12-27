import json
import re
import adaptive_cards.card as ac
from datetime import datetime, timedelta
from typing import Any, List, Dict
from microsoft.teams.apps import ActivityContext
from microsoft.teams.api import MessageActivityInput

from enums import BotAction
from services.graph_service import GraphService
from services.openai_service import OpenAIService

def create_user_selection_card(ambiguous_users: List[Dict], search_term: str) -> dict:
    """Створює картку для вибору користувача з неоднозначних результатів"""
    facts = []
    for idx, user in enumerate(ambiguous_users):
        # Гарантуємо, що value завжди буде рядком
        email_value = user.get('mail') or user.get('userPrincipalName') or 'No email'
        facts.append(ac.Fact(
            title=f"{idx + 1}. {user.get('displayName', 'Unknown')}",
            value=str(email_value)  # Переконуємося що це рядок
        ))
    
    card = ac.AdaptiveCard(
        version="1.4",
        body=[
            ac.TextBlock(text="Знайдено кілька користувачів", weight="Bolder", size="Medium", color="Accent"),
            ac.TextBlock(text=f"Для '{search_term}' знайдено кілька співпадінь. Оберіть потрібного:", wrap=True),
            ac.Container(style="emphasis", items=[ac.FactSet(facts=facts)]),
        ],
        actions=[
            ac.ActionSubmit(
                title=f"Обрати: {user.get('displayName')}",
                data={"action": "select_user", "user_id": user.get('id'), "user_data": user}
            ) for user in ambiguous_users
        ]
    )
    return card.to_dict()

def create_meeting_proposal_card(meeting_data: Dict) -> dict:
    """Створює картку з запропонованим часом зустрічі"""
    start_time = meeting_data.get('start_time')
    end_time = meeting_data.get('end_time')
    participants = meeting_data.get('participants', [])
    subject = meeting_data.get('subject', 'Meeting')
    duration = meeting_data.get('duration', 30)
    agenda = meeting_data.get('agenda')
    
    # Форматуємо час
    if isinstance(start_time, str):
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    else:
        start_dt = start_time
    
    if isinstance(end_time, str):
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    else:
        end_dt = end_time
    
    time_str = start_dt.strftime("%Y-%m-%d %H:%M") + " - " + end_dt.strftime("%H:%M")
    
    participants_list = "\n".join([f"• {p.get('displayName', p.get('name', 'Unknown'))}" for p in participants])
    
    # Формуємо body картки
    card_body = [
        ac.TextBlock(text="Запропонований час зустрічі", weight="Bolder", size="Medium", color="Accent"),
        ac.Container(style="emphasis", items=[
            ac.FactSet(facts=[
                ac.Fact(title="Тема:", value=subject),
                ac.Fact(title="Дата та час:", value=time_str),
                ac.Fact(title="Тривалість:", value=f"{duration} хвилин"),
            ])
        ]),
        ac.TextBlock(text="Учасники:", weight="Bolder", size="Small"),
        ac.TextBlock(text=participants_list, wrap=True),
    ]
    
    # Додаємо агенду якщо вона є
    if agenda:
        card_body.append(ac.TextBlock(text="Агенда:", weight="Bolder", size="Small", spacing="Medium"))
        card_body.append(ac.TextBlock(text=agenda, wrap=True, spacing="None"))
    
    card = ac.AdaptiveCard(
        version="1.4",
        body=card_body,
        actions=[
            ac.ActionSubmit(
                title="✅ Підтвердити",
                data={"action": "confirm_meeting", "meeting_data": meeting_data}
            ),
            ac.ActionSubmit(
                title="🔄 Знайти інший час",
                data={"action": "regenerate_time", "meeting_data": meeting_data}
            )
        ]
    )
    return card.to_dict()

async def resolve_users(participants: List[Dict], graph_service: GraphService, openai_service: OpenAIService = None, requester_id: str = None) -> Dict[str, Any]:
    """Вирішує імена користувачів та знаходить їх ID"""
    resolved_users = []
    ambiguous_selections = []
    
    for participant in participants:
        name = participant.get('name', '').strip()
        p_type = participant.get('type', 'name')
        
        # Якщо користувач вказує себе
        if p_type == "self" or name.lower() in ["me", "я", "мене", "мною"]:
            if requester_id:
                # Отримуємо дані про користувача
                user_result = await graph_service.get_user_by_id(requester_id)
                if user_result.get("success"):
                    resolved_users.append({
                        "id": requester_id,
                        "displayName": user_result["user"].get("displayName"),
                        "mail": user_result["user"].get("mail"),
                        "userPrincipalName": user_result["user"].get("userPrincipalName")
                    })
            continue
        
        # Шукаємо користувача
        search_result = await graph_service.search_users(name, limit=5)
        
        users = []
        exact_match_found = False
        
        if search_result.get("success"):
            users = search_result.get("users", [])
            
            # Перевіряємо, чи є точне співпадіння для повного імені
            # Якщо шукали повне ім'я і знайшли рівно 1 користувача - це точне співпадіння
            if len(name.split()) >= 2 and len(users) == 1:
                # Перевіряємо, чи displayName містить обидва слова
                user_display_name = users[0].get('displayName', '').lower()
                name_lower = name.lower()
                name_parts = name_lower.split()
                
                # Якщо всі частини імені присутні в displayName - це точне співпадіння
                if all(part in user_display_name for part in name_parts):
                    exact_match_found = True
                    print(f"✅ Знайдено точне співпадіння: {users[0].get('displayName')}")
        
        # Якщо точний пошук не дав результатів - пробуємо fallback по першій букві
        if len(users) == 0:
            print(f"⚠️ Точний пошук не знайшов '{name}', пробую fallback по першій букві...")
            fallback_result = await graph_service.search_users_by_first_letter(name, limit=20)
            
            if fallback_result.get("success"):
                fallback_users = fallback_result.get("users", [])
                print(f"📋 Знайдено {len(fallback_users)} користувачів через fallback пошук")
                
                if len(fallback_users) == 0:
                    return {"success": False, "error": f"Користувача '{name}' не знайдено"}
                elif len(fallback_users) == 1:
                    # Один результат - використовуємо його
                    users = fallback_users
                elif len(fallback_users) <= 10:
                    # 2-10 користувачів - показуємо картку вибору
                    ambiguous_selections.append({
                        "search_term": name,
                        "users": fallback_users
                    })
                    # Продовжуємо обробку нижче
                else:
                    # Багато користувачів - спробуємо використати LLM для вибору
                    if openai_service:
                        print(f"🤖 Використовую LLM для вибору найближчого користувача з {len(fallback_users)}...")
                        llm_result = await openai_service.select_best_user_match(name, fallback_users)
                        
                        if llm_result.get("success"):
                            selected_user = llm_result.get("user")
                            confidence = llm_result.get("confidence", "medium")
                            print(f"✅ LLM вибрав: {selected_user.get('displayName')} (confidence: {confidence})")
                            users = [selected_user]
                        else:
                            # LLM не зміг вибрати - показуємо перші 10
                            ambiguous_selections.append({
                                "search_term": name,
                                "users": fallback_users[:10]
                            })
                    else:
                        # Немає LLM - показуємо перші 10
                        ambiguous_selections.append({
                            "search_term": name,
                            "users": fallback_users[:10]
                        })
            else:
                return {"success": False, "error": f"Користувача '{name}' не знайдено"}
        
        # Обробка результатів
        if exact_match_found:
            # Точне співпадіння знайдено - використовуємо його
            resolved_users.append(users[0])
        elif len(users) == 0:
            if ambiguous_selections:
                # Вже додано в ambiguous_selections
                pass
            else:
                return {"success": False, "error": f"Користувача '{name}' не знайдено"}
        elif len(users) == 1:
            # Однозначне співпадіння
            resolved_users.append(users[0])
        else:
            # Неоднозначність - спробуємо використати LLM для вибору, якщо є багато варіантів
            if len(users) <= 5 and openai_service:
                print(f"🤖 Використовую LLM для вибору найближчого користувача з {len(users)}...")
                llm_result = await openai_service.select_best_user_match(name, users)
                
                if llm_result.get("success"):
                    selected_user = llm_result.get("user")
                    confidence = llm_result.get("confidence", "medium")
                    print(f"✅ LLM вибрав: {selected_user.get('displayName')} (confidence: {confidence})")
                    
                    # Якщо впевненість висока - використовуємо автоматично
                    if confidence == "high":
                        resolved_users.append(selected_user)
                    else:
                        # Інакше показуємо картку вибору
                        ambiguous_selections.append({
                            "search_term": name,
                            "users": users
                        })
                else:
                    # LLM не зміг вибрати - показуємо картку вибору
                    ambiguous_selections.append({
                        "search_term": name,
                        "users": users
                    })
            else:
                # Багато користувачів або немає LLM - показуємо картку вибору
                ambiguous_selections.append({
                    "search_term": name,
                    "users": users
                })
    
    if ambiguous_selections:
        return {
            "success": False,
            "ambiguous": True,
            "selections": ambiguous_selections,
            "resolved": resolved_users
        }
    
    return {"success": True, "users": resolved_users}

async def find_available_time(users: List[Dict], preferred_date: str, preferred_time: str, duration: int, graph_service: GraphService) -> Dict[str, Any]:
    """Знаходить вільний час для зустрічі"""
    # Парсимо дату та час
    now = datetime.utcnow()
    
    # Визначаємо початкову дату
    if preferred_date:
        preferred_date_lower = preferred_date.lower()
        if preferred_date_lower in ["tomorrow", "завтра"]:
            start_date = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
        elif "monday" in preferred_date_lower or "понеділок" in preferred_date_lower:
            days_ahead = (7 - now.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            start_date = (now + timedelta(days=days_ahead)).replace(hour=9, minute=0, second=0, microsecond=0)
        elif "friday" in preferred_date_lower or "п'ятниця" in preferred_date_lower or "пятниця" in preferred_date_lower:
            days_ahead = (4 - now.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            start_date = (now + timedelta(days=days_ahead)).replace(hour=9, minute=0, second=0, microsecond=0)
        else:
            # Спробуємо розпарсити як ISO дату
            try:
                start_date = datetime.fromisoformat(preferred_date)
            except:
                start_date = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    else:
        start_date = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    
    # Визначаємо час
    if preferred_time:
        preferred_time_lower = preferred_time.lower()
        
        # Обробка діапазону часу (наприклад, "12:30-15:00" або "з 12:30 до 15:00")
        if "-" in preferred_time or "до" in preferred_time_lower:
            # Беремо початковий час з діапазону
            if "-" in preferred_time:
                time_parts = preferred_time.split("-")
                start_time_str = time_parts[0].strip()
            else:
                # "з 12:30 до 15:00"
                time_match = re.search(r'(\d{1,2}):(\d{2})', preferred_time)
                if time_match:
                    start_time_str = time_match.group(0)
                else:
                    start_time_str = preferred_time
        else:
            start_time_str = preferred_time
        
        # Парсимо початковий час
        if "pm" in start_time_str.lower() or "пп" in start_time_str.lower():
            hour = int(start_time_str.replace("pm", "").replace("пп", "").strip().split(":")[0])
            if hour < 12:
                hour += 12
            minute = 0
            if ":" in start_time_str:
                minute = int(start_time_str.split(":")[1].replace("pm", "").replace("пп", "").strip())
            start_date = start_date.replace(hour=hour, minute=minute)
        elif "am" in start_time_str.lower() or "дп" in start_time_str.lower():
            hour = int(start_time_str.replace("am", "").replace("дп", "").strip().split(":")[0])
            minute = 0
            if ":" in start_time_str:
                minute = int(start_time_str.split(":")[1].replace("am", "").replace("дп", "").strip())
            start_date = start_date.replace(hour=hour, minute=minute)
        elif ":" in start_time_str:
            parts = start_time_str.split(":")
            start_date = start_date.replace(hour=int(parts[0]), minute=int(parts[1]))
        elif start_time_str.isdigit():
            start_date = start_date.replace(hour=int(start_time_str), minute=0)
    
    end_date = start_date + timedelta(days=7)  # Шукаємо в наступні 7 днів
    
    # Отримуємо email адреси користувачів
    user_emails = [u.get('mail') or u.get('userPrincipalName') for u in users if u.get('mail') or u.get('userPrincipalName')]
    
    if not user_emails:
        return {"success": False, "error": "Не вдалося отримати email адреси користувачів"}
    
    # Використовуємо першого користувача як організатора
    organizer_id = users[0].get('id') or users[0].get('userPrincipalName')
    
    # Шукаємо вільні слоти
    result = await graph_service.find_free_slots(organizer_id, user_emails, start_date, end_date, duration)
    
    if not result.get("success"):
        return result
    
    suggestions = result.get("suggestions", [])
    
    if not suggestions:
        return {"success": False, "error": "Не знайдено вільних слотів для всіх учасників"}
    
    # Беремо перший запропонований час
    best_suggestion = suggestions[0]
    meeting_time = best_suggestion.get('meetingTimeSlot', {})
    
    return {
        "success": True,
        "start_time": meeting_time.get('start', {}).get('dateTime'),
        "end_time": meeting_time.get('end', {}).get('dateTime'),
        "confidence": best_suggestion.get('confidence', 'medium')
    }

async def handle_action(ctx: ActivityContext, action: str, action_data: dict = None,
                       graph_service: GraphService = None, openai_service: OpenAIService = None,
                       requester_id: str = None):
    """Обробляє дії з карток календаря"""
    if action == BotAction.SELECT_USER.value:
        # Користувач обрав користувача з неоднозначних результатів
        user_data = action_data.get("user_data")
        await ctx.send(f"✅ Обрано: {user_data.get('displayName')} ({user_data.get('mail')})")
        # TODO: Продовжити процес створення зустрічі з обраним користувачем
        
    elif action == BotAction.CONFIRM_MEETING.value:
        # Підтвердження створення зустрічі
        meeting_data = action_data.get("meeting_data")
        participants = meeting_data.get("participants", [])
        subject = meeting_data.get("subject", "Meeting")
        agenda = meeting_data.get("agenda")
        start_time_str = meeting_data.get("start_time")
        end_time_str = meeting_data.get("end_time")
        
        # Парсимо час
        start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
        
        # Отримуємо email адреси учасників
        attendee_emails = [p.get('mail') or p.get('userPrincipalName') for p in participants if p.get('mail') or p.get('userPrincipalName')]
        
        # Створюємо зустріч (використовуємо першого учасника як організатора)
        if not attendee_emails:
            await ctx.send("❌ Помилка: не вдалося визначити учасників")
            return
        
        organizer_id = participants[0].get('id') if participants else None
        if not organizer_id:
            # Якщо немає ID, використовуємо email
            organizer_id = attendee_emails[0]
        
        result = await graph_service.create_meeting(
            organizer_id=organizer_id,
            attendees=attendee_emails,
            subject=subject,
            start_time=start_time,
            end_time=end_time,
            agenda=agenda
        )
        
        if result.get("success"):
            event = result.get("event", {})
            agenda_text = f"\n📋 Агенда: {agenda}" if agenda else ""
            await ctx.send(f"✅ **Зустріч успішно створено!**\n\n📅 {subject}\n🕐 {start_time.strftime('%Y-%m-%d %H:%M')}\n👥 {len(attendee_emails)} учасників{agenda_text}")
        else:
            await ctx.send(f"❌ Помилка створення зустрічі: {result.get('error')}")
            
    elif action == BotAction.REGENERATE_TIME.value:
        # Перегенерація часу
        meeting_data = action_data.get("meeting_data")
        await ctx.send("🔄 Шукаю інший вільний час...")
        # TODO: Реалізувати перегенерацію

async def run_flow(ctx: ActivityContext, intent_data: dict,
                  openai_service: OpenAIService = None,
                  graph_service: GraphService = None,
                  requester_id: str = None):
    """Головний flow календаря: аналіз часу -> пошук слотів -> бронювання"""
    
    # Перевіряємо, чи це дія з картки
    if ctx.activity.value and "action" in ctx.activity.value:
        action = ctx.activity.value["action"]
        await handle_action(ctx, action, ctx.activity.value, graph_service, openai_service, requester_id)
        return
    
    # Парсимо запит на зустріч
    user_text = ctx.activity.text
    
    if not openai_service:
        await ctx.send("❌ Помилка: сервіс OpenAI не ініціалізовано")
        return
    
    meeting_data = await openai_service.parse_meeting_request(user_text)
    
    if "error" in meeting_data:
        await ctx.send("⚠️ Не зрозумів запит на зустріч. Будь ласка, уточніть учасників та час.")
        return
    
    # Витягуємо дані
    participants_raw = meeting_data.get("participants", [])
    preferred_date = meeting_data.get("preferredDate")
    preferred_time = meeting_data.get("preferredTime")
    duration = meeting_data.get("duration", 30)
    subject = meeting_data.get("subject", "Meeting")
    agenda = meeting_data.get("agenda")
    include_requester = meeting_data.get("includeRequester", False)
    
    if not participants_raw:
        await ctx.send("⚠️ Не вказано учасників зустрічі. Будь ласка, вкажіть учасників (наприклад, @John Smith або просто Smith).")
        return
    
    # Вирішуємо користувачів
    await ctx.send("🔍 Шукаю учасників...")
    resolve_result = await resolve_users(participants_raw, graph_service, openai_service, requester_id)
    
    if not resolve_result.get("success"):
        if resolve_result.get("ambiguous"):
            # Показуємо картку вибору для першої неоднозначності
            selections = resolve_result.get("selections", [])
            if selections:
                first_ambiguous = selections[0]
                card = create_user_selection_card(first_ambiguous["users"], first_ambiguous["search_term"])
                await ctx.send(MessageActivityInput(
                    type="message",
                    attachments=[{
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "content": card
                    }]
                ))
            return
        else:
            await ctx.send(f"❌ {resolve_result.get('error', 'Помилка пошуку користувачів')}")
            return
    
    resolved_users = resolve_result.get("users", [])
    
    # Додаємо організатора якщо потрібно
    if include_requester and requester_id:
        user_result = await graph_service.get_user_by_id(requester_id)
        if user_result.get("success"):
            requester_user = user_result["user"]
            # Перевіряємо чи вже не додано
            if not any(u.get('id') == requester_id for u in resolved_users):
                resolved_users.append({
                    "id": requester_id,
                    "displayName": requester_user.get("displayName"),
                    "mail": requester_user.get("mail"),
                    "userPrincipalName": requester_user.get("userPrincipalName")
                })
    
    if not resolved_users:
        await ctx.send("❌ Не вдалося знайти жодного учасника")
        return
    
    # Шукаємо вільний час
    await ctx.send("📅 Перевіряю календарі та шукаю вільний час...")
    time_result = await find_available_time(
        resolved_users,
        preferred_date,
        preferred_time,
        duration,
        graph_service
    )
    
    if not time_result.get("success"):
        await ctx.send(f"❌ {time_result.get('error', 'Не вдалося знайти вільний час')}")
        return
    
    # Створюємо картку з запропонованим часом
    meeting_proposal = {
        "start_time": time_result.get("start_time"),
        "end_time": time_result.get("end_time"),
        "participants": resolved_users,
        "subject": subject,
        "duration": duration,
        "agenda": agenda
    }
    
    card = create_meeting_proposal_card(meeting_proposal)
    await ctx.send(MessageActivityInput(
        type="message",
        attachments=[{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": card
        }]
    ))
