"""
Find Time Action - Encapsulates logic for finding meeting slots.

This Action class implements the Command pattern for the "Find Time" use case.
It orchestrates:
1. Date parsing (using global utils)
2. Participant resolution (using UserSearchService)
3. Availability search (using GraphService)
4. Result mapping (to Domain Models)
"""
import logging
from typing import List, Optional, Union, Dict, Tuple
from datetime import datetime, timedelta

from services.graph_service import GraphService
from services.user_search import UserSearchService
from utils.date_parser import parse_date
from ..models import (
    SchedulingResult, 
    Participant, 
    TimeSlot, 
    FindTimeRequest,
    FindTimeData
)


logger = logging.getLogger("HRBot")


class FindTimeAction:
    """
    Action class responsible for finding available meeting slots.
    """

    def __init__(self, graph_service: GraphService, user_search_service: UserSearchService):
        self.graph_service = graph_service
        self.user_search_service = user_search_service

    async def execute(self, request: FindTimeRequest) -> SchedulingResult:
        """
        Executes the find time logic.
        
        Args:
            requester_id: ID of the user requesting the meeting
            participant_names: List of names or emails
            subject: Meeting subject
            duration_minutes: Duration in minutes
            start_date: Start of search window (optional)
            end_date: End of search window (optional)
            
        Returns:
            SchedulingResult containing found slots or error
        """
        try:
            # 1. Prepare Date Window
            search_start, search_end = self._get_search_window(
                request.start_date, 
                request.end_date
                )
            
            # 2. Resolve Participants
            resolved_participants = await self._resolve_participants(request.participant_names)
            
            # Extract valid emails for Graph API
            participant_emails = [
                p.get_email() for p in resolved_participants if p.get_email()
            ]
            
            if not participant_emails:
                return SchedulingResult(
                    success=False,
                    error="Не вдалося знайти жодного учасника з валідною поштою.",
                    resolved_participants=resolved_participants
                )
            
            # 3. Find free slots using GraphService
            # Note: requester_id is used as the organizer
            result = await self.graph_service.find_free_slots(
                organizer_id=request.requester_id,
                user_emails=participant_emails,
                start_date=search_start,
                end_date=search_end,
                duration_minutes=request.duration_minutes
            )
            
            if not result.get("success"):
                return SchedulingResult(
                    success=False,
                    error=result.get("error", "Помилка пошуку вільних слотів"),
                    resolved_participants=resolved_participants
                )
            
            # 4. Map Results to Domain Models
            slots = self._map_suggestions_to_slots(
                suggestions=result.get("suggestions", []),
                resolved_participants=resolved_participants
            )
            
            if not slots:
                return SchedulingResult(
                    success=False,
                    error="На жаль, не знайдено вільного часу для всіх учасників.",
                    resolved_participants=resolved_participants
                )
            
            response_data = FindTimeData(
                slots=slots,
                subject=request.subject,
                duration=request.duration_minutes,
                participants=resolved_participants
            )
            
            return SchedulingResult(
                success=True,
                data=response_data,
                resolved_participants=resolved_participants
            )
            
        except Exception as e:
            logger.error(f"Error in FindTimeAction.execute: {e}", exc_info=True)
            return SchedulingResult(
                success=False,
                error=f"Системна помилка пошуку часу: {str(e)}"
            )

    # =========================================================================
    # Private Helpers
    # =========================================================================

    def _get_search_window(
        self, 
        start: Optional[Union[str, datetime]], 
        end: Optional[Union[str, datetime]]
    ) -> Tuple[datetime, datetime]:
        """Calculates valid start and end datetimes for search."""
        # Use parse_date utility for robust parsing
        parsed_start = parse_date(start) if start else None
        
        # Default start to now if not provided or invalid
        if not parsed_start:
            parsed_start = datetime.utcnow()
            
        parsed_end = parse_date(end) if end else None
        
        # Default end to +7 days if not provided
        if not parsed_end:
            parsed_end = parsed_start + timedelta(days=7)
            
        return parsed_start, parsed_end

    async def _resolve_participants(self, names: List[str]) -> List[Participant]:
        """Resolves a list of names/emails to Participant objects."""
        resolved = []
        
        logger.info(f"🕵️ [FindTimeAction] Resolving {len(names)} participants: {names}")

        for name in names:
            # 1. Try to find user in Azure AD via UserSearchService
            logger.info(f"🔎 [FindTimeAction] Searching for '{name}'...")
            
            try:
                search_result = await self.user_search_service.search_user(name)
                logger.info(f"📄 [FindTimeAction] Search result for '{name}': {search_result}")

                if search_result.get("success") and search_result.get("user"):
                    user = search_result["user"]
                    logger.info(f"✅ [FindTimeAction] Resolved '{name}' -> {user.get('displayName')} ({user.get('mail')})")
                    
                    resolved.append(Participant(
                        id=user.get("id"),
                        displayName=user.get("displayName"),
                        mail=user.get("mail"),
                        userPrincipalName=user.get("userPrincipalName"),
                        givenName=user.get("givenName"),
                        surname=user.get("surname")
                    ))
                
                elif search_result.get("ambiguous"):
                    # ПРОБЛЕМА ТУТ: Ми поки що ігноруємо неоднозначні результати
                    logger.warning(f"⚠️ [FindTimeAction] Ambiguous result for '{name}'. Dropping user for now.")
                    # TODO: Повернути це в контролер, щоб запитати користувача
                    
                else:
                    logger.warning(f"❌ [FindTimeAction] User '{name}' not found via SearchService. Error: {search_result.get('error')}")
                    
                    # 2. Fallback: If it looks like an email, use it as is
                    if "@" in name:
                        logger.info(f"📧 [FindTimeAction] Using '{name}' as raw email fallback.")
                        resolved.append(Participant(
                            displayName=name, 
                            mail=name, 
                            email=name
                        ))
                    else:
                        logger.warning(f"🗑️ [FindTimeAction] Dropping '{name}' completely.")

            except Exception as e:
                logger.error(f"💥 [FindTimeAction] Exception searching for '{name}': {e}", exc_info=True)

        logger.info(f"🏁 [FindTimeAction] Total resolved: {len(resolved)}")            
        return resolved

    def _map_suggestions_to_slots(
        self, 
        suggestions: List[Dict], 
        resolved_participants: List[Participant]
    ) -> List[TimeSlot]:
        """Maps raw Graph API suggestions to TimeSlot models."""
        slots = []
        
        for suggestion in suggestions:
            meeting_time = suggestion.get("meetingTimeSlot", {})
            start = meeting_time.get("start", {}).get("dateTime")
            end = meeting_time.get("end", {}).get("dateTime")
            
            if not start or not end:
                continue

            # Identify who is busy in this specific slot (Partial availability)
            busy_people = []
            attendee_availability = suggestion.get("attendeeAvailability", [])
            
            for attendee in attendee_availability:
                # Check availability status (busy, oof, tentantive treated as busy here)
                availability = attendee.get("availability")
                if availability in ["busy", "tentative", "oof"]:
                    email = attendee.get("emailAddress", {}).get("address", "")
                    
                    # Match email back to our resolved participant object
                    # Using a generator expression to find the first match
                    participant = next(
                        (p for p in resolved_participants if p.get_email() and p.get_email().lower() == email.lower()),
                        Participant(displayName=email, mail=email, email=email) # Fallback if not in resolved list
                    )
                    busy_people.append(participant)
            
            slots.append(TimeSlot(
                start_time=start,
                end_time=end,
                confidence=str(suggestion.get("confidence", "medium")), # Ensure string
                busy_participants=busy_people if busy_people else None
            ))
            
        return slots
    

__all__ = ["FindTimeAction"]

