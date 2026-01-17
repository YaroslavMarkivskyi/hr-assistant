import logging
from typing import Any

from enums.bot import BotModule
from features.time_off.enums import TimeOffAction, LeaveType
from features.time_off.service import TimeOffService
from features.time_off.schemas import SubmitLeaveActionPayload
from features.scheduling.models import ActionContext # Використовуємо загальний контекст

logger = logging.getLogger("HRBot")

class TimeOffActionHandler:
    """
    Handles button clicks (Adaptive Card Actions) for Time Off module.
    """
    
    def __init__(self, service: TimeOffService):
        self._service = service

    async def handle(self, ctx: ActionContext) -> None:
        """
        Routes the action to the specific method based on payload.action.
        """
        action = ctx.payload.action
        logger.info(f"🔘 TimeOff Action triggered: {action}")

        if action == TimeOffAction.SUBMIT_REQUEST:
            await self._handle_submit_request(ctx)
            
        elif action == TimeOffAction.CANCEL_MY_REQUEST:
            await self._handle_cancel_request(ctx)
            
        else:
            logger.warning(f"⚠️ Unknown TimeOff action: {action}")
            await ctx.ctx.send_activity("Ця дія поки що не підтримується.")

    async def _handle_submit_request(self, ctx: ActionContext) -> None:
        """
        Processing the 'Submit' button from the Leave Request Form.
        """
        # 1. Отримуємо дані з форми (вони лежать в ctx.payload.data)
        # Adaptive Cards надсилають всі input.id як ключі словника
        raw_data = ctx.payload.data or {}
        
        # Очищаємо дані від системних полів (типу "msteams", "action", "module")
        # Нам потрібні: leave_type, date_start, date_end, reason
        
        try:
            # 2. Валідація через Pydantic (використовуємо схему, яку ми створили раніше)
            # Input.Date повертає рядок "YYYY-MM-DD"
            payload = SubmitLeaveActionPayload(**raw_data)
        except Exception as e:
            logger.error(f"❌ Validation error: {e}")
            await ctx.ctx.send_activity(f"Помилка даних форми: {str(e)}")
            return

        await ctx.ctx.send_typing_activity()

        # 3. Виклик бізнес-логіки
        result = await self._service.create_request(
            user_id=ctx.requester_id,
            leave_type=payload.leave_type,
            start_date=payload.start_date,
            end_date=payload.end_date,
            reason=payload.reason
        )

        # 4. Відповідь користувачу
        if result.success:
            # Можна показати картку успіху або просто текст
            await ctx.ctx.send_activity(
                f"✅ **Заявку створено!**\n\n"
                f"Тип: {payload.leave_type.value}\n"
                f"Дати: {payload.start_date} — {payload.end_date}\n"
                f"Статус: Pending"
            )
        else:
            await ctx.ctx.send_activity(f"❌ Не вдалося створити заявку: {result.error}")

    async def _handle_cancel_request(self, ctx: ActionContext) -> None:
        """
        Processing the 'Cancel' button from the Cancellation Card.
        """
        # Дані передаються в 'context' об'єкті payload
        # data: { action: ..., context: { request_id: "123" } }
        action_context = ctx.payload.context or {}
        request_id = action_context.get("request_id")
        
        if not request_id:
            await ctx.ctx.send_activity("❌ Помилка: не знайдено ID заявки.")
            return

        await ctx.ctx.send_typing_activity()

        result = await self._service.cancel_request(
            user_id=ctx.requester_id,
            request_id=request_id
        )

        if result.success:
            # Adaptive Card дозволяє оновлювати картку "на льоту", але поки просто пишемо текст
            await ctx.ctx.send_activity(f"🗑️ Заявку #{request_id} успішно скасовано.")
        else:
            await ctx.ctx.send_activity(f"❌ Помилка скасування: {result.error}")
            

__all__ = ["TimeOffActionHandler"]

