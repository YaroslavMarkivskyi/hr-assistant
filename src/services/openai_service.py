import json
import os
from typing import Dict, Any, Optional, List
from microsoft.teams.ai import ChatPrompt, ListMemory
from microsoft.teams.openai import OpenAICompletionsAIModel

from utils.retry import retry_with_backoff
from interfaces.ai_service import AIService
from models.ai import AIResponse

class OpenAIService:
    """
    OpenAI implementation of AIService protocol.
    
    Uses OpenAI's GPT models via microsoft-teams-openai SDK.
    Implements all methods required by AIService protocol.
    """
    def __init__(self, config):
        self.model = OpenAICompletionsAIModel(
            key=config.OPENAI_API_KEY,
            model=config.OPENAI_MODEL_NAME
        )
        self.config = config
        self.candidate_instructions = self._load_candidate_instructions()
        self.intent_instructions = self._load_intent_instructions()
        self.calendar_instructions = self._load_calendar_instructions()

    def _load_candidate_instructions(self) -> str:
        """Loads instructions for parsing candidate data"""
        try:
            path = os.path.join(os.path.dirname(__file__), "..", "prompts", "candidate.txt")
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "You are an HR Onboarding Assistant. Extract structured data from the user's input (resume text or candidate description). Return a valid JSON object with fields: firstName, lastName, jobTitle, department, emailNickname, personalEmail, phoneNumber, address. If no candidate data found, return {\"error\": \"No candidate data found\"}."

    def _load_intent_instructions(self) -> str:
        """Loads instructions for intent detection"""
        try:
            path = os.path.join(os.path.dirname(__file__), "..", "prompts", "intent.txt")
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return """You are an intent classifier for an HR bot.
Analyze the user's message and determine their intent.

IMPORTANT RULES:
1. "onboarding" - User provides NEW candidate/employee data (name, email, phone, job title, resume) AND wants to CREATE a new account.
2. "schedule_meeting" - User wants to schedule a meeting, book calendar, find time slot.
3. "chat" - Greetings, general questions, friendly conversation.
4. "unknown" - Use ONLY when you cannot determine the user's intent with any confidence.

Return ONLY a valid JSON object with this structure:
{
  "intent": "onboarding" | "schedule_meeting" | "chat" | "unknown",
  "entities": {}
}"""

    def _load_calendar_instructions(self) -> str:
        """Loads instructions for parsing meeting requests"""
        try:
            path = os.path.join(os.path.dirname(__file__), "..", "prompts", "calendar.txt")
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "You are a meeting scheduling assistant. Extract structured data from the user's message about scheduling a meeting. Return a valid JSON object with fields: participants (array), preferredDate, preferredTime, duration, subject, includeRequester. If no meeting data found, return {\"error\": \"No meeting data found\"}."

    async def detect_intent(self, user_message: str) -> Dict[str, Any]:
        """Визначає намір користувача з повідомлення.

        Returns a dict compatible with legacy callers, but internally uses
        AIResponse Pydantic model to validate structure and module/intent
        consistency.
        """
        # Get retry config from settings
        max_retries = getattr(self.config, 'AI_MAX_RETRIES', 2)
        base_delay = getattr(self.config, 'AI_RETRY_DELAY_SECONDS', 1.0)
        
        # Apply retry decorator with config values
        decorated_func = retry_with_backoff(max_retries=max_retries, base_delay=base_delay)(
            self._detect_intent_impl
        )
        return await decorated_func(user_message)
    
    async def _detect_intent_impl(self, user_message: str) -> Dict[str, Any]:
        """Internal implementation of detect_intent (called by retry decorator)"""
        chat_prompt = ChatPrompt(self.model)
        chat_result = await chat_prompt.send(
            input=user_message,
            memory=ListMemory(),
            instructions=self.intent_instructions
        )
        
        try:
            clean_json = chat_result.response.content.replace("```json", "").replace("```", "").strip()
            raw = json.loads(clean_json)

            # Map raw JSON into AIResponse for strict validation.
            # Backward-compat: infer module for legacy flat intents when possible.
            if "module" not in raw:
                # Simple heuristic: map legacy flat intents to modules when possible.
                intent = raw.get("intent", "unknown")
                if intent in [
                    "onboarding",
                    "schedule_meeting",
                    "welcome_checklist",
                    "offboarding",
                ]:
                    raw["module"] = "people_ops"
                elif intent in [
                    "request_vacation",
                    "check_vacation_balance",
                    "view_pending_requests",
                ]:
                    raw["module"] = "time_off"
                elif intent in ["ask_question"]:
                    raw["module"] = "knowledge_base"
                elif intent in ["request_access", "request_equipment"]:
                    raw["module"] = "service_desk"

            # Provide defaults for new fields if missing
            raw.setdefault("entities", {})
            raw.setdefault("confidence", 0.0)
            raw.setdefault("language", "en")  # Default to English if not detected

            ai_response = AIResponse.model_validate(raw)

            # Return a plain dict so existing code continues to work.
            # For general intents like "chat"/"unknown", module may be None.
            return {
                "module": ai_response.module.value if ai_response.module else None,
                "intent": ai_response.intent,
                "entities": ai_response.entities,
                "confidence": ai_response.confidence,
                "reasoning": ai_response.reasoning,
                "language": ai_response.language,
            }
        except Exception as e:
            # Якщо не вдалося розпарсити або валідувати, повертаємо unknown як fallback
            print(f"⚠️ Intent detection error: {e}")
            return {
                "intent": "unknown",
                "entities": {},
                "confidence": 0.0,
                "reasoning": None,
                "language": "en",  # Default to English on error
            }

    async def parse_candidate_data(self, user_message: str) -> Dict[str, Any]:
        """Парсить дані кандидата з повідомлення"""
        # Get retry config from settings
        max_retries = getattr(self.config, 'AI_MAX_RETRIES', 2)
        base_delay = getattr(self.config, 'AI_RETRY_DELAY_SECONDS', 1.0)
        
        # Apply retry decorator with config values
        decorated_func = retry_with_backoff(max_retries=max_retries, base_delay=base_delay)(
            self._parse_candidate_data_impl
        )
        return await decorated_func(user_message)
    
    async def _parse_candidate_data_impl(self, user_message: str) -> Dict[str, Any]:
        """Internal implementation of parse_candidate_data (called by retry decorator)"""
        chat_prompt = ChatPrompt(self.model)
        chat_result = await chat_prompt.send(
            input=user_message,
            memory=ListMemory(),
            instructions=self.candidate_instructions
        )
        
        try:
            clean_json = chat_result.response.content.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(clean_json)
            return parsed
        except Exception as e:
            return {"error": f"Failed to parse candidate data: {str(e)}"}

    async def parse_meeting_request(
        self, 
        user_message: str, 
        current_date: str | None = None
    ) -> Dict[str, Any]:
        """Парсить дані про зустріч з повідомлення"""
        # Get retry config from settings
        max_retries = getattr(self.config, 'AI_MAX_RETRIES', 2)
        base_delay = getattr(self.config, 'AI_RETRY_DELAY_SECONDS', 1.0)
        
        # Apply retry decorator with config values
        decorated_func = retry_with_backoff(max_retries=max_retries, base_delay=base_delay)(
            self._parse_meeting_request_impl
        )
        return await decorated_func(user_message, current_date)
    
    async def _parse_meeting_request_impl(
        self, 
        user_message: str, 
        current_date: str | None = None
    ) -> Dict[str, Any]:
        """Internal implementation of parse_meeting_request (called by retry decorator)"""
        # Add current date context to instructions
        from datetime import datetime
        
        # Use provided date or current system date
        if current_date:
            # Parse provided date string (YYYY-MM-DD)
            try:
                date_obj = datetime.strptime(current_date, "%Y-%m-%d")
            except ValueError:
                # Invalid format, fall back to current date
                date_obj = datetime.now()
        else:
            date_obj = datetime.now()
        
        current_date_str = date_obj.strftime("%Y-%m-%d")
        current_weekday = date_obj.strftime("%A")  # Monday, Tuesday, etc.
        current_weekday_uk = {
            "Monday": "понеділок", "Tuesday": "вівторок", "Wednesday": "середа",
            "Thursday": "четвер", "Friday": "п'ятниця", "Saturday": "субота", "Sunday": "неділя"
        }.get(current_weekday, current_weekday)
        
        instructions_with_date = f"""{self.calendar_instructions}

CURRENT DATE CONTEXT:
- Today's date: {current_date_str}
- Today's weekday: {current_weekday} ({current_weekday_uk})
- When parsing days of week:
  - If user says "next [day]" / "наступний [day]" → always next week's date in ISO format (YYYY-MM-DD)
  - If user says "[day]" without "next" → this week if day hasn't passed, otherwise next week (in ISO format YYYY-MM-DD)
  - Always return ISO format (YYYY-MM-DD) for dates, not just day names like "Tuesday" or "вівторок"
"""
        
        chat_prompt = ChatPrompt(self.model)
        chat_result = await chat_prompt.send(
            input=user_message,
            memory=ListMemory(),
            instructions=instructions_with_date
        )
        
        try:
            clean_json = chat_result.response.content.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(clean_json)
            return parsed
        except Exception as e:
            return {"error": f"Failed to parse meeting data: {str(e)}"}

    async def select_best_user_match(self, user_query: str, users: List[Dict]) -> Dict[str, Any]:
        """Вибирає найближчого користувача зі списку через LLM"""
        if not users:
            return {"error": "No users provided"}
        
        if len(users) == 1:
            return {"success": True, "user": users[0], "confidence": "high"}
        
        # Get retry config from settings
        max_retries = getattr(self.config, 'AI_MAX_RETRIES', 2)
        base_delay = getattr(self.config, 'AI_RETRY_DELAY_SECONDS', 1.0)
        
        # Apply retry decorator with config values
        decorated_func = retry_with_backoff(max_retries=max_retries, base_delay=base_delay)(
            self._select_best_user_match_impl
        )
        return await decorated_func(user_query, users)
    
    async def _select_best_user_match_impl(self, user_query: str, users: List[Dict]) -> Dict[str, Any]:
        """Internal implementation of select_best_user_match (called by retry decorator)"""
        # Формуємо список користувачів для LLM
        users_list = []
        for idx, user in enumerate(users):
            users_list.append({
                "index": idx,
                "displayName": user.get("displayName", ""),
                "givenName": user.get("givenName", ""),
                "surname": user.get("surname", ""),
                "mail": user.get("mail", ""),
                "userPrincipalName": user.get("userPrincipalName", "")
            })
        
        instructions = f"""You are a user matching assistant. The user searched for: "{user_query}"

Here are the found users:
{json.dumps(users_list, indent=2, ensure_ascii=False)}

Your task is to select the BEST matching user based on the search query. Consider:
- Name similarity (first name, last name, full name)
- Spelling variations
- Transliteration (Ukrainian to English)

Return ONLY a JSON object with this structure:
{{
    "index": <number> - the index of the best matching user (0-based),
    "confidence": "high" | "medium" | "low" - how confident you are in the match,
    "reason": "<brief explanation>"
}}

If no user matches well, return: {{"error": "No good match found"}}

DO NOT write any conversational text. DO NOT use markdown formatting. Just return the raw JSON string."""
        
        chat_prompt = ChatPrompt(self.model)
        chat_result = await chat_prompt.send(
            input=user_query,
            memory=ListMemory(),
            instructions=instructions
        )
        
        try:
            clean_json = chat_result.response.content.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean_json)
            
            if "error" in result:
                return result
            
            selected_index = result.get("index")
            if selected_index is not None and 0 <= selected_index < len(users):
                return {
                    "success": True,
                    "user": users[selected_index],
                    "confidence": result.get("confidence", "medium"),
                    "reason": result.get("reason", "")
                }
            else:
                return {"error": "Invalid index returned"}
                
        except Exception as e:
            return {"error": f"Failed to parse LLM response: {str(e)}"}
    
    async def generate_text(
        self,
        user_message: str,
        system_prompt: str | None = None,
        context: str | None = None
    ) -> str:
        """
        Generate unstructured text response for conversational chat.
        
        Uses OpenAI to generate natural language responses for general conversation,
        fallback scenarios, or knowledge base queries.
        """
        # Get retry config from settings
        max_retries = getattr(self.config, 'AI_MAX_RETRIES', 2)
        base_delay = getattr(self.config, 'AI_RETRY_DELAY_SECONDS', 1.0)
        
        # Apply retry decorator with config values
        decorated_func = retry_with_backoff(max_retries=max_retries, base_delay=base_delay)(
            self._generate_text_impl
        )
        return await decorated_func(user_message, system_prompt, context)
    
    async def _generate_text_impl(
        self,
        user_message: str,
        system_prompt: str | None = None,
        context: str | None = None
    ) -> str:
        """Internal implementation of generate_text (called by retry decorator)"""
        # Default system prompt if none provided
        default_prompt = """You are a friendly and helpful HR Onboarding Assistant for Microsoft Teams.
You help employees with onboarding, scheduling meetings, time off requests, and general HR questions.
Be concise, professional, but warm and approachable. Respond in the same language as the user."""
        
        instructions = system_prompt or default_prompt
        
        # Add context if provided
        if context:
            instructions += f"\n\nContext:\n{context}"
        
        chat_prompt = ChatPrompt(self.model)
        chat_result = await chat_prompt.send(
            input=user_message,
            memory=ListMemory(),
            instructions=instructions
        )
        
        # Return the text response directly (no JSON parsing needed)
        return chat_result.response.content.strip()

