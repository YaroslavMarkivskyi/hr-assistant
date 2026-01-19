"""
Adaptive Card views for Scheduling module.

All UI rendering logic is centralized here.
Uses strongly typed ViewModels to ensure data consistency.
"""
import logging
import json
from datetime import datetime
from typing import List, Dict, Any

import adaptive_cards.card as ac

from core.enums.bot import SchedulingAction
from .schemas import (
    FindTimeViewModel, 
    ScheduleViewModel, 
    DailyBriefingViewModel, 
    BookingConfirmationViewModel,
    TimeSlot
)

logger = logging.getLogger("HRBot")


def create_find_time_card(vm: FindTimeViewModel) -> dict:
    """
    Create Adaptive Card showing available time slots.
    Payloads are structured to match BookSlotContext model.
    """
    card_body = [
        ac.TextBlock(
            text="Знайдено вільні слоти",
            weight="Bolder",
            size="Medium",
            color="Accent"
        ),
        ac.TextBlock(
            text=f"Тема: {vm.subject}",
            weight="Bolder",
            size="Small"
        ),
        ac.TextBlock(
            text=f"Тривалість: {vm.duration} хвилин",
            size="Small",
            spacing="Small"
        )
    ]
    
    # Серіалізуємо учасників один раз, щоб передати їх у контекст бронювання.
    # Pydantic model_dump(mode='json') зробить їх словниками.
    participants_json = [p.model_dump(mode='json') for p in vm.participants]

    # Відображаємо перші 3 слоти (або 5, як налаштуєте)
    display_limit = 3
    for idx, slot in enumerate(vm.slots[:display_limit]):  
        
        # Форматування дати для відображення (UI)
        try:
            start_dt = datetime.fromisoformat(slot.start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(slot.end_time.replace('Z', '+00:00'))
            time_str = f"{start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}"
            date_str = start_dt.strftime("%d.%m.%Y")
        except ValueError:
            time_str = "Invalid Time"
            date_str = ""
        
        # Інформація про зайнятість (якщо це soft-booking)
        busy_info = ""
        if slot.busy_participants:
            busy_names = [p.get_display_name() for p in slot.busy_participants]
            busy_info = f" (Конфлікт: {', '.join(busy_names)})"
        
        # 👇 Підготовка контексту для дії BOOK_SLOT
        # Ця структура має точно відповідати моделі BookSlotContext
        book_context = {
            "start": slot.start_time,  # ISO string
            "end": slot.end_time,      # ISO string
            "subject": vm.subject,
            "duration": vm.duration,
            "participants": participants_json
        }

        card_body.append(
            ac.Container(
                style="emphasis",
                spacing="Medium",
                items=[
                    ac.TextBlock(
                        text=f"📅 {date_str} | ⏰ {time_str}{busy_info}",
                        weight="Bolder",
                        wrap=True
                    ),
                    ac.ActionSet(
                        actions=[
                            ac.ActionSubmit(
                                title="✅ Забронювати",
                                data={
                                    "action": SchedulingAction.BOOK_SLOT, # "book_slot"
                                    "context": book_context  # <--- ВАЖЛИВО: Дані всередині context
                                }
                            )
                        ]
                    )
                ]
            )
        )
    
    # Кнопка "Show more"
    if len(vm.slots) > display_limit:
        # Для пагінації беремо дату останнього показаного слота
        last_slot = vm.slots[display_limit-1]
        
        show_more_context = {
            "subject": vm.subject,
            "duration": vm.duration,
            "next_page_date": last_slot.start_time,
            "participants": participants_json
        }

        card_body.append(
            ac.ActionSet(
                actions=[
                    ac.ActionSubmit(
                        title="Показати більше варіантів",
                        data={
                            "action": SchedulingAction.SHOW_MORE_SLOTS,
                            "context": show_more_context
                        }
                    )
                ]
            )
        )
    
    card = ac.AdaptiveCard(version="1.4", body=card_body)
    return clean_card_dict(card.to_dict())


def create_booking_confirmation_card(vm: BookingConfirmationViewModel) -> dict:
    """Create booking confirmation card."""
    card_body = [
        ac.TextBlock(
            text="✅ Зустріч успішно створено!",
            weight="Bolder",
            size="Medium",
            color="Good" # Green color
        ),
        ac.FactSet(
            facts=[
                ac.Fact(title="Тема:", value=vm.subject or "Meeting"),
                ac.Fact(title="Тривалість:", value=f"{vm.duration} хв"),
            ]
        )
    ]
    
    if vm.start_time_str:
         card_body.append(ac.TextBlock(text=f"⏰ Час: {vm.start_time_str}", size="Small", weight="Bolder"))

    # Список учасників
    if vm.participants:
        # Формуємо список імен
        names = [p.get_display_name() for p in vm.participants]
        # Якщо учасників багато, обрізаємо
        if len(names) > 5:
            names = names[:5] + [f"...ще {len(names)-5}"]
            
        participants_text = ", ".join(names)
        
        card_body.append(ac.TextBlock(text="👥 Учасники:", weight="Bolder", size="Small", spacing="Medium"))
        card_body.append(ac.TextBlock(text=participants_text, wrap=True, isSubtle=True))
    
    # Дії після створення
    actions = [
        ac.ActionSubmit(
            title="📋 Деталі в календарі",
            data={"action": SchedulingAction.VIEW_CALENDAR_DETAILS}
        ),
        ac.ActionSubmit(
            title="❌ Скасувати",
            data={
                "action": SchedulingAction.CANCEL_MEETING,
                # Тут можна передати ID зустрічі, якщо він є у ViewModel
                # "context": {"meeting_id": vm.meeting_id} 
            }
        )
    ]
    
    card = ac.AdaptiveCard(version="1.4", body=card_body, actions=actions)
    return clean_card_dict(card.to_dict())


def create_daily_briefing_card(vm: DailyBriefingViewModel) -> dict:
    """Create daily briefing card."""
    card_body = [
        ac.TextBlock(
            text=f"📅 Ваш календар на {vm.date_str}",
            weight="Bolder",
            size="Medium",
            color="Accent"
        ),
        ac.FactSet(
            facts=[
                ac.Fact(title="Зустрічей:", value=str(vm.meetings_count)),
            ]
        )
    ]
    
    if vm.next_meeting_text:
        card_body.append(
            ac.TextBlock(
                text=vm.next_meeting_text,
                weight="Bolder",
                size="Small",
                color="Attention"
            )
        )
    
    if vm.free_windows_text:
        card_body.append(ac.TextBlock(text="🕐 Вільні вікна:", weight="Bolder", size="Small", spacing="Medium"))
        card_body.append(ac.TextBlock(text=vm.free_windows_text, wrap=True, isSubtle=True))
    
    actions = [
        ac.ActionSubmit(
            title="📋 Повний розклад",
            data={"action": SchedulingAction.VIEW_CALENDAR_DETAILS}
        )
    ]
    
    card = ac.AdaptiveCard(version="1.4", body=card_body, actions=actions)
    return clean_card_dict(card.to_dict())


def create_schedule_card(vm: ScheduleViewModel) -> dict:
    """Create timeline schedule card."""
    card_body = [
        ac.TextBlock(
            text=f"📅 Розклад: {vm.employee_name}",
            weight="Bolder",
            size="Medium",
            color="Accent"
        ),
        ac.TextBlock(
            text=f"Дата: {vm.date_str}",
            size="Small",
            spacing="Small",
            isSubtle=True
        )
    ]
    
    if not vm.grouped_slots:
         card_body.append(ac.TextBlock(text="Запланованих зустрічей немає.", isSubtle=True))
    
    for slot in vm.grouped_slots:
        # Очікуємо slot як dict (якщо це raw structure) або об'єкт
        # Для універсальності припускаємо dict, бо Timeline logic специфічна
        start = slot.get('start', '')
        end = slot.get('end', '')
        subject = slot.get('subject', 'Busy')
        
        card_body.append(
            ac.Container(
                style="emphasis",
                spacing="Small",
                items=[
                    ac.TextBlock(
                        text=f"🕒 {start} - {end} | {subject}", 
                        wrap=True,
                        size="Small"
                    )
                ]
            )
        )
    
    card = ac.AdaptiveCard(version="1.4", body=card_body)
    return clean_card_dict(card.to_dict())


def create_workshop_card() -> dict:
    """Static placeholder card."""
    card_body = [
        ac.TextBlock(
            text="🎓 Створення воркшопу",
            weight="Bolder",
            size="Medium",
            color="Accent"
        ),
        ac.TextBlock(
            text="Цей функціонал дозволить створити подію для великої групи людей.",
            wrap=True,
            spacing="Small"
        ),
        ac.TextBlock(
            text="⚠️ Наразі в розробці.",
            wrap=True,
            spacing="Medium",
            color="Warning"
        )
    ]
    
    actions = [
        ac.ActionSubmit(
            title="Повідомити коли буде готово", 
            data={"action": SchedulingAction.CONFIRM_WORKSHOP}
        )
    ]
    card = ac.AdaptiveCard(version="1.4", body=card_body, actions=actions)
    return clean_card_dict(card.to_dict())


def clean_card_dict(card_dict: dict) -> dict:
    """
    Recursively clean card dict to ensure JSON serializability.
    Prevents errors if Pydantic objects or non-serializable types slip in.
    """
    def _clean_value(value):
        if value is None:
            return None
        elif isinstance(value, (str, int, float, bool)):
            return value
        elif isinstance(value, dict):
            return {str(k): _clean_value(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [_clean_value(item) for item in value]
        else:
            # Fallback for unexpected objects (like Enum or Pydantic models not dumped)
            return str(value)
    
    return _clean_value(card_dict)