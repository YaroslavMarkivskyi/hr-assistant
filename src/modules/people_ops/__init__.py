"""
People Ops модуль - управління персоналом
Підмодулі:
- onboarding: Створення акаунтів для нових співробітників
- scheduling: Призначення перших зустрічей
- welcome_checklist: Welcome Checklist для новачків
- offboarding: Звільнення співробітників
"""
# Імпортуємо існуючі фічі як підмодулі
import sys
from pathlib import Path

# Додаємо шлях до features для імпорту існуючих модулів
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Імпортуємо існуючі фічі
from features import onboarding, calendar

__all__ = ['onboarding', 'calendar']

