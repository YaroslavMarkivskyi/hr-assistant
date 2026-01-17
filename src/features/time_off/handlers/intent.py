import logging
from typing import Dict, Callable, Any

# Enums
from enums.bot.intents import TimeOffIntent
from ..enums import LeaveRequestStatus

# Services & Models
from ..service import TimeOffService
from features.scheduling.schemas import IntentContext

# Mapper & Views
from ..mappers import TimeOffMapper
from ..views import (
    create_balance_card,
    create_leave_request_form,
    create_requests_list_card,
    create_cancellation_card
)

logger = logging.getLogger("HRBot")

class TimeOffIntentHandler:
    """
    Handles text commands (Intents) for Time Off module.
    Orchestrates: 
    1. Routing (via Map)
    2. Data Preparation (via Mapper)
    3. Service Call (Business Logic)
    4. View Generation (Adaptive Cards)
    """
    
    def __init__(self, service: TimeOffService):
        self._service = service
        
        self._handlers: Dict[TimeOffIntent, Callable[[IntentContext], Any]] = {
            TimeOffIntent.CHECK_BALANCE: self._handle_check_balance,
            TimeOffIntent.REQUEST_LEAVE: self._handle_request_leave,
            TimeOffIntent.VIEW_REQUESTS: self._handle_view_requests,
            TimeOffIntent.CANCEL_REQUEST: self._handle_cancel_request,
        }

    async def handle(self, ctx: IntentContext) -> None:
        """Main entry point for intents processing."""
        intent = ctx.user_intent.intent
        
        handler = self._handlers.get(intent)
        
        if handler:
            try:
                await handler(ctx)
            except Exception as e:
                logger.error(f"❌ Error in TimeOff handler for {intent}: {e}", exc_info=True)
                await ctx.ctx.send_activity(f"Сталася помилка при обробці вашого запиту: {str(e)}")
        else:
            logger.warning(f"⚠️ Unhandled TimeOff intent: {intent}")
            await ctx.ctx.send_activity("Я зрозумів, що це стосується відпусток, але поки не вмію виконувати цю конкретну дію.")

    # =========================================================================
    # SPECIFIC HANDLERS
    # =========================================================================

    async def _handle_check_balance(self, request: IntentContext) -> None:
        """
        User asks: "Скільки в мене днів відпустки?"
        Action: Fetch balance -> Map to VM -> Show Balance Card.
        """
        await request.ctx.send_typing_activity()
        
        user_id = request.requester_id
        year = request.user_intent.entities.get("year")
        
        # 1. Отримуємо доменну модель (EmployeeBalance)
        balance = await self._service.get_balance(user_id, year)
        
        if not balance:
            await request.ctx.send_activity("❌ Не вдалося отримати дані про ваші баланси.")
            return

        # 2. Мапимо у ViewModel (готуємо цифри для відображення)
        balance_vm = TimeOffMapper.map_to_balance_view(balance)

        # 3. Генеруємо та відправляємо картку
        card = create_balance_card(balance_vm)
        await request.ctx.send_adaptive_card(card)

    async def _handle_request_leave(self, request: IntentContext) -> None:
        """
        User asks: "Хочу у відпустку з понеділка"
        Action: 
        1. AI 2nd pass via Mapper (extract dates/type).
        2. Generate Input Form (Adaptive Card).
        """
        await request.ctx.send_typing_activity()

        # 1. Mapper викликає AI та повертає готовий LeaveRequestFormViewModel
        form_data = await TimeOffMapper.map_to_leave_form_data(request)

        # 2. Генеруємо картку з передзаповненими даними
        card = create_leave_request_form(form_data)
        
        # 3. Відправляємо користувачу
        await request.ctx.send_adaptive_card(card)

    async def _handle_view_requests(self, request: IntentContext) -> None:
        """
        User asks: "Мої заявки"
        Action: Fetch requests -> Show List Card.
        """
        await request.ctx.send_typing_activity()
        
        requests = await self._service.get_user_requests(request.requester_id)
        
        if not requests:
            await request.ctx.send_activity("📭 Історія заявок порожня.")
            return

        # Генеруємо картку списку (List View)
        # В'юха приймає список доменних моделей LeaveRequest напряму
        card = create_requests_list_card(requests)
        await request.ctx.send_adaptive_card(card)

    async def _handle_cancel_request(self, request: IntentContext) -> None:
        """
        User asks: "Скасувати заявку"
        Action: Fetch PENDING requests -> Show Card with Cancel Buttons.
        """
        await request.ctx.send_typing_activity()
        
        # Фільтруємо тільки ті, що можна скасувати
        pending_requests = await self._service.get_user_requests(
            request.requester_id, 
            status=LeaveRequestStatus.PENDING
        )
        
        if not pending_requests:
            await request.ctx.send_activity("🤷‍♂️ У вас немає активних заявок, які можна скасувати.")
            return

        card = create_cancellation_card(pending_requests)
        await request.ctx.send_adaptive_card(card)

__all__ = ["TimeOffIntentHandler"]