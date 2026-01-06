"""
Adaptive Card views for Scheduling module.

All UI rendering logic is centralized here.
Now uses strongly typed ViewModels instead of raw dicts.
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, List

import adaptive_cards.card as ac

from .models import (
    FindTimeViewModel, 
    ScheduleViewModel, 
    DailyBriefingViewModel, 
    BookingConfirmationViewModel,
    TimeSlot
)

logger = logging.getLogger("HRBot")


def create_find_time_card(vm: FindTimeViewModel) -> dict:
    """
    Create Adaptive Card showing available time slots using ViewModel.
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
    
    # Add slots (Top 3)
    # Ми впевнені, що vm.slots - це список об'єктів TimeSlot (Pydantic)
    for idx, slot in enumerate(vm.slots[:3]):  
        
        # Форматування дати
        start_dt = datetime.fromisoformat(slot.start_time.replace('Z', '+00:00'))
        time_str = start_dt.strftime("%d.%m.%Y %H:%M")
        
        busy_info = ""
        if slot.busy_participants:
            busy_names = [p.get_display_name() for p in slot.busy_participants]
            busy_info = f" (Зайняті: {', '.join(busy_names)})"
        
        card_body.append(
            ac.Container(
                style="emphasis",
                spacing="Medium",
                items=[
                    ac.TextBlock(
                        text=f"Слот {idx + 1}: {time_str}{busy_info}",
                        weight="Bolder"
                    ),
                    ac.ActionSet(
                        actions=[
                            ac.ActionSubmit(
                                title="✅ Забронювати",
                                data={
                                    "action": "book_slot",
                                    "slot_index": idx,
                                    "slot_data": slot.model_dump() # Pydantic метод
                                }
                            )
                        ]
                    )
                ]
            )
        )
    
    # "Show more" button
    if len(vm.slots) > 3:
        # Серіалізуємо всі слоти для передачі в payload кнопки
        all_slots_dict = [s.model_dump() for s in vm.slots]
        
        card_body.append(
            ac.ActionSet(
                actions=[
                    ac.ActionSubmit(
                        title="Показати більше варіантів",
                        data={
                            "action": "show_more_slots", 
                            "context": { # Запаковуємо в context, як ми і планували в ActionContext
                                "all_slots": all_slots_dict,
                                "subject": vm.subject,
                                "duration": vm.duration
                            }
                        }
                    )
                ]
            )
        )
    
    card = ac.AdaptiveCard(version="1.4", body=card_body)
    return clean_card_dict(card.to_dict())


def create_booking_confirmation_card(vm: BookingConfirmationViewModel) -> dict:
    """Create booking confirmation card using ViewModel."""
    card_body = [
        ac.TextBlock(
            text="Підтвердження бронювання",
            weight="Bolder",
            size="Medium",
            color="Accent"
        ),
        ac.FactSet(
            facts=[
                ac.Fact(title="Тема:", value=vm.subject or "Meeting"),
                ac.Fact(title="Тривалість:", value=f"{vm.duration} хвилин"),
            ]
        )
    ]
    
    if vm.start_time_str:
         card_body.append(ac.TextBlock(text=f"Час: {vm.start_time_str}", size="Small"))

    # Participants list
    if vm.participants:
        participants_text = "\n".join([f"• {p.get_display_name()}" for p in vm.participants])
        card_body.append(ac.TextBlock(text="Учасники:", weight="Bolder", size="Small"))
        card_body.append(ac.TextBlock(text=participants_text, wrap=True))
    
    actions = [
        ac.ActionSubmit(
            title="✅ Підтвердити бронювання",
            data={"action": "confirm_booking"}
        ),
        ac.ActionSubmit(
            title="➕ Додати групу",
            data={"action": "add_group"}
        )
    ]
    
    card = ac.AdaptiveCard(version="1.4", body=card_body, actions=actions)
    return clean_card_dict(card.to_dict())


def create_daily_briefing_card(vm: DailyBriefingViewModel) -> dict:
    """
    Create daily briefing card using ViewModel.
    Note: Calculations are removed from here. The View just renders strings.
    """
    card_body = [
        ac.TextBlock(
            text=f"📅 Ваш календар на {vm.date_str}", # ViewModel вже має відформатовану дату
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
                text=vm.next_meeting_text, # Напр: "⏰ Наступна зустріч через 15 хв: Daily"
                weight="Bolder",
                size="Small",
                color="Attention"
            )
        )
    
    if vm.free_windows_text:
        card_body.append(ac.TextBlock(text="🕐 Вільні вікна:", weight="Bolder", size="Small"))
        card_body.append(ac.TextBlock(text=vm.free_windows_text, wrap=True))
    
    actions = [
        ac.ActionSubmit(
            title="📋 Деталі календаря",
            data={"action": "view_calendar_details"}
        )
    ]
    
    card = ac.AdaptiveCard(version="1.4", body=card_body, actions=actions)
    return clean_card_dict(card.to_dict())


def create_schedule_card(vm: ScheduleViewModel) -> dict:
    """Create Adaptive Card with employee schedule timeline using ViewModel."""
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
            spacing="Small"
        )
    ]
    
    # Add timeline items
    for slot in vm.grouped_slots:
        # Тут можна також зробити типи, але для простоти поки dict
        time_str = f"🕘 {slot.get('start')} - {slot.get('end')}"
        subject = slot.get('subject', 'Busy')
        
        card_body.append(
            ac.Container(
                style="emphasis",
                spacing="Small",
                items=[
                    ac.TextBlock(text=f"{time_str} | {subject}", wrap=True)
                ]
            )
        )
    
    card = ac.AdaptiveCard(version="1.4", body=card_body)
    return clean_card_dict(card.to_dict())


def create_workshop_card() -> dict:
    """Static card, no ViewModel needed yet."""
    card_body = [
        ac.TextBlock(
            text="Створення воркшопу/лекції",
            weight="Bolder",
            size="Medium",
            color="Accent"
        ),
        ac.TextBlock(
            text="⚠️ Функціонал в розробці. Будь ласка, використовуйте текстові команди.",
            wrap=True,
            spacing="Medium"
        )
    ]
    
    actions = [ac.ActionSubmit(title="✅ Створити воркшоп", data={"action": "confirm_workshop"})]
    card = ac.AdaptiveCard(version="1.4", body=card_body, actions=actions)
    return clean_card_dict(card.to_dict())


def clean_card_dict(card_dict: dict) -> dict:
    """
    Recursively clean card dict to ensure JSON serializability.
    Keeps helper logic centralized.
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
            try:
                # Try simple string conversion for generic objects
                return str(value)
            except Exception:
                return str(value)
    
    cleaned = _clean_value(card_dict)
    return cleaned