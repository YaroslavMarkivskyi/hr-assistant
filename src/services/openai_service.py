import json
import os
from typing import Dict, Any, Optional, List
from microsoft.teams.ai import ChatPrompt, ListMemory
from microsoft.teams.openai import OpenAICompletionsAIModel

class OpenAIService:
    def __init__(self, config):
        self.model = OpenAICompletionsAIModel(
            key=config.OPENAI_API_KEY,
            model=config.OPENAI_MODEL_NAME
        )
        self.candidate_instructions = self._load_candidate_instructions()
        self.intent_instructions = self._load_intent_instructions()
        self.calendar_instructions = self._load_calendar_instructions()

    def _load_candidate_instructions(self) -> str:
        """Завантажує інструкції для парсингу кандидатів"""
        try:
            path = os.path.join(os.path.dirname(__file__), "..", "instructions.txt")
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "You are an HR Onboarding Assistant. Extract structured data from the user's input (resume text or candidate description). Return a valid JSON object with fields: firstName, lastName, jobTitle, department, emailNickname, personalEmail, phoneNumber, address. If no candidate data found, return {\"error\": \"No candidate data found\"}."

    def _load_intent_instructions(self) -> str:
        """Інструкції для визначення наміру користувача"""
        return """You are an intent classifier for an HR bot.
Analyze the user's message and determine their intent.

IMPORTANT RULES:
1. "onboarding" - User provides NEW candidate/employee data (name, email, phone, job title, resume) AND wants to CREATE a new account. Keywords: "create account", "new employee", "new hire", "onboard", "candidate", resume data.
2. "schedule_meeting" - User wants to schedule a meeting, book calendar, find time slot. Keywords: "schedule", "meeting", "book", "calendar", "@mention", "find time", "when available", "зустріч", "зустрітися", "запланувати", "признач ондобдинг для X на Y" (assign onboarding for X on Y), "assign onboarding to X on Y".
3. "chat" - Greetings, general questions, friendly conversation.
4. "unknown" - Use ONLY when you cannot determine the user's intent with any confidence. Do not guess - if uncertain, use "unknown".

CRITICAL: 
- If message mentions "признач ондобдинг" (assign onboarding) or "assign onboarding" WITH a date/time (на понеділок, on Monday, tomorrow, etc.) -> "schedule_meeting"
- If message mentions "признач ондобдинг" WITHOUT date/time -> "schedule_meeting" (default to scheduling)
- If message contains ONLY a name/person reference WITHOUT candidate data (email, phone, job title) AND mentions "assign", "признач" WITHOUT date -> could be "schedule_meeting" or "chat" depending on context

Examples:
- "Create account for John Doe, email: john@example.com, position: Developer" -> "onboarding"
- "John Doe, john@example.com, Developer" -> "onboarding"  
- "признач ондобдинг для Andriy Verbeko на понеділок" -> "schedule_meeting" (has date)
- "признач ондобдинг для Andriy Verbeko" -> "schedule_meeting" (assign onboarding = schedule meeting)
- "assign onboarding to John tomorrow" -> "schedule_meeting"
- "Schedule meeting with @John tomorrow at 2pm" -> "schedule_meeting"
- "Заплануй зустріч з Іваном завтра" -> "schedule_meeting"
- "Привіт" -> "chat"
- "Що ти вмієш?" -> "chat"
- "asdfghjkl" (gibberish) -> "unknown"
- "???" (unclear) -> "unknown"

Return ONLY a JSON object with this structure:
{
    "intent": "onboarding" | "schedule_meeting" | "chat" | "unknown",
    "entities": {}
}

If you cannot determine the user's intent with confidence, use "unknown" instead of guessing.

DO NOT write any conversational text. DO NOT use markdown formatting. Just return the raw JSON string."""

    def _load_calendar_instructions(self) -> str:
        """Завантажує інструкції для парсингу зустрічей"""
        try:
            path = os.path.join(os.path.dirname(__file__), "..", "instructions_calendar.txt")
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "You are a meeting scheduling assistant. Extract structured data from the user's message about scheduling a meeting. Return a valid JSON object with fields: participants (array), preferredDate, preferredTime, duration, subject, includeRequester. If no meeting data found, return {\"error\": \"No meeting data found\"}."

    async def detect_intent(self, user_message: str) -> Dict[str, Any]:
        """Визначає намір користувача з повідомлення"""
        chat_prompt = ChatPrompt(self.model)
        chat_result = await chat_prompt.send(
            input=user_message,
            memory=ListMemory(),
            instructions=self.intent_instructions
        )
        
        try:
            clean_json = chat_result.response.content.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(clean_json)
            # Валідуємо intent - якщо невалідний, повертаємо unknown
            valid_intents = ["onboarding", "schedule_meeting", "welcome_checklist", "offboarding",
                           "request_vacation", "check_vacation_balance", "ask_question",
                           "request_access", "request_equipment", "chat", "unknown"]
            if parsed.get("intent") not in valid_intents:
                print(f"⚠️ Invalid intent detected: {parsed.get('intent')}, using 'unknown'")
                parsed["intent"] = "unknown"
            return parsed
        except Exception as e:
            # Якщо не вдалося розпарсити, повертаємо unknown як fallback
            print(f"⚠️ Intent detection error: {e}")
            return {"intent": "unknown", "entities": {}}

    async def parse_candidate_data(self, user_message: str) -> Dict[str, Any]:
        """Парсить дані кандидата з повідомлення"""
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

    async def parse_meeting_request(self, user_message: str) -> Dict[str, Any]:
        """Парсить дані про зустріч з повідомлення"""
        chat_prompt = ChatPrompt(self.model)
        chat_result = await chat_prompt.send(
            input=user_message,
            memory=ListMemory(),
            instructions=self.calendar_instructions
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

