"""
Adaptive Cards generators for Time Off module.
RETURNS DICTIONARIES, NOT ATTACHMENTS.
"""
import json
from typing import List, Dict, Any # Змінено типи

# Ми більше не використовуємо CardFactory, бо повертаємо сирий dict
# from botbuilder.schema import Attachment
# from botbuilder.core import CardFactory

from .schemas import (
    BalanceViewModel, 
    LeaveRequestFormViewModel, 
    LeaveRequest
)
from .enums import LeaveType, LeaveRequestStatus, TimeOffAction

COLOR_GOOD = "Good"       
COLOR_WARNING = "Warning" 
COLOR_ATTENTION = "Attention" 
COLOR_DEFAULT = "Default"

# 👇 Змінено Return Type Hint на Dict[str, Any]
def create_balance_card(model: BalanceViewModel) -> Dict[str, Any]:
    """
    Generates a card showing user's leave balances.
    """
    
    vacation_str = f"**{model.vacation_available}** з {model.vacation_total} днів"
    sick_str = f"**{model.sick_available}** з {model.sick_total} днів"
    days_off_str = f"Використано: **{model.days_off_used}** (Ліміт: {model.days_off_total})"

    card_data = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.5",
        "body": [
            {
                "type": "TextBlock",
                "text": f"📊 Баланс відпусток ({model.year})",
                "weight": "Bolder",
                "size": "Medium"
            },
            {
                "type": "Container",
                "items": [
                    {
                        "type": "FactSet",
                        "facts": [
                            {"title": "🏖️ Відпустка:", "value": vacation_str},
                            {"title": "🤒 Лікарняні:", "value": sick_str},
                            {"title": "🏠 Day Off:", "value": days_off_str}
                        ]
                    }
                ],
                "style": "emphasis",
                "bleed": True
            }
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "📅 Створити заявку",
                "data": {
                    "msteams": {
                        "type": "messageBack",
                        "text": "Хочу у відпустку"
                    }
                }
            }
        ]
    }
    # 👇 ПОВЕРТАЄМО СЛОВНИК НАПРЯМУ
    return card_data 


def create_leave_request_form(model: LeaveRequestFormViewModel) -> Dict[str, Any]:
    """
    Generates an input form for creating a leave request.
    """
    
    leave_type_value = model.default_type.value if model.default_type else "vacation"

    card_data = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.5",
        "body": [
            {
                "type": "TextBlock",
                "text": "📝 Нова заявка",
                "size": "Large",
                "weight": "Bolder"
            },
            {
                "type": "TextBlock",
                "text": "Заповніть деталі вашої відсутності:",
                "isSubtle": True,
                "wrap": True
            },
            {
                "type": "Input.ChoiceSet",
                "id": "leave_type",
                "label": "Тип відсутності",
                "value": leave_type_value,
                "style": "compact",
                "choices": [
                    {"title": "🏖️ Основна відпустка", "value": "vacation"},
                    {"title": "🤒 Лікарняний", "value": "sick"},
                    {"title": "🏠 Day Off (за власний рах.)", "value": "day_off"}
                ],
                "isRequired": True,
                "errorMessage": "Будь ласка, оберіть тип."
            },
            {
                "type": "ColumnSet",
                "columns": [
                    {
                        "type": "Column",
                        "width": "stretch",
                        "items": [
                            {
                                "type": "Input.Date",
                                "id": "date_start",
                                "label": "Початок",
                                "value": model.default_start_date,
                                "isRequired": True
                            }
                        ]
                    },
                    {
                        "type": "Column",
                        "width": "stretch",
                        "items": [
                            {
                                "type": "Input.Date",
                                "id": "date_end",
                                "label": "Кінець",
                                "value": model.default_end_date,
                                "isRequired": True
                            }
                        ]
                    }
                ]
            },
            {
                "type": "Input.Text",
                "id": "reason",
                "label": "Причина / Коментар",
                "isMultiline": True,
                "placeholder": "Наприклад: сімейні обставини...",
                "value": model.default_reason
            }
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "✅ Відправити",
                "style": "positive",
                "data": {
                    "action": TimeOffAction.SUBMIT_REQUEST,
                    "module": "timeoff"
                }
            }
        ]
    }
    return card_data


def create_requests_list_card(requests: List[LeaveRequest]) -> Dict[str, Any]:
    """
    Generates a list of recent requests with statuses.
    """
    body_items = [
        {
            "type": "TextBlock",
            "text": "📂 Історія заявок",
            "size": "Medium",
            "weight": "Bolder"
        }
    ]

    if not requests:
        body_items.append({
            "type": "TextBlock",
            "text": "У вас ще немає заявок.",
            "isSubtle": True
        })
    else:
        for req in requests[:5]:
            status_config = {
                LeaveRequestStatus.APPROVED: (COLOR_GOOD, "✅"),
                LeaveRequestStatus.PENDING: (COLOR_WARNING, "⏳"),
                LeaveRequestStatus.REJECTED: (COLOR_ATTENTION, "❌"),
                LeaveRequestStatus.CANCELLED: (COLOR_DEFAULT, "🚫"),
                LeaveRequestStatus.COMPLETED: (COLOR_DEFAULT, "🏁"),
            }.get(req.status, (COLOR_DEFAULT, "❓"))
            
            color, icon = status_config

            type_map = {
                LeaveType.VACATION: "Відпустка",
                LeaveType.SICK: "Лікарняний",
                LeaveType.DAY_OFF: "Day Off"
            }
            type_text = type_map.get(req.leave_type, req.leave_type)

            item_container = {
                "type": "Container",
                "style": "default",
                "separator": True,
                "spacing": "Medium",
                "items": [
                    {
                        "type": "ColumnSet",
                        "columns": [
                            {
                                "type": "Column",
                                "width": "stretch",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": f"**{type_text}**",
                                        "wrap": True
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": f"{req.start_date} — {req.end_date} ({req.days_count} дн.)",
                                        "size": "Small",
                                        "isSubtle": True
                                    }
                                ]
                            },
                            {
                                "type": "Column",
                                "width": "auto",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": f"{icon} {req.status.value.title()}",
                                        "color": color,
                                        "weight": "Bolder",
                                        "horizontalAlignment": "Right"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            body_items.append(item_container)

    card_data = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.5",
        "body": body_items
    }
    return card_data


def create_cancellation_card(requests: List[LeaveRequest]) -> Dict[str, Any]:
    """
    Shows list of PENDING requests with a 'Cancel' button for each.
    """
    body_items = [
        {
            "type": "TextBlock",
            "text": "🚫 Скасування заявки",
            "size": "Medium",
            "weight": "Bolder",
            "color": "Attention"
        },
        {
            "type": "TextBlock",
            "text": "Оберіть заявку, яку бажаєте скасувати:",
            "isSubtle": True,
            "wrap": True
        }
    ]

    for req in requests:
        item = {
            "type": "Container",
            "separator": True,
            "items": [
                {
                    "type": "ColumnSet",
                    "columns": [
                        {
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": f"**{req.leave_type.value.upper()}** ({req.start_date})",
                                    "wrap": True
                                },
                                {
                                    "type": "TextBlock",
                                    "text": "Статус: Pending ⏳",
                                    "isSubtle": True,
                                    "size": "Small"
                                }
                            ]
                        },
                        {
                            "type": "Column",
                            "width": "auto",
                            "items": [
                                {
                                    "type": "ActionSet",
                                    "actions": [
                                        {
                                            "type": "Action.Submit",
                                            "title": "Скасувати",
                                            "style": "destructive",
                                            "data": {
                                                "action": TimeOffAction.CANCEL_MY_REQUEST,
                                                "module": "timeoff",
                                                "context": {
                                                    "request_id": str(req.id)
                                                }
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        body_items.append(item)

    card_data = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.5",
        "body": body_items
    }
    return card_data