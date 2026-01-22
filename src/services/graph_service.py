from __future__ import annotations
import logging

from datetime import datetime
from typing import Dict, Any, List, Optional, TYPE_CHECKING

from core.utils.security_utils import generate_strong_password
from core.utils.text_utils import is_cyrillic, transliterate_for_azure
from schemas.service_response import ServiceResponse

from azure.identity.aio import ClientSecretCredential

from msgraph import GraphServiceClient
from msgraph.generated.users.users_request_builder import UsersRequestBuilder

from msgraph.generated.models.user import User
from msgraph.generated.models.password_profile import PasswordProfile
from msgraph.generated.models.attendee import Attendee
from msgraph.generated.models.email_address import EmailAddress
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.event import Event
from msgraph.generated.models.date_time_time_zone import DateTimeTimeZone
from msgraph.generated.models.time_constraint import TimeConstraint
from msgraph.generated.models.time_slot import TimeSlot
from msgraph.generated.models.location import Location
from msgraph.generated.models.online_meeting_provider_type import OnlineMeetingProviderType

from msgraph.generated.users.item.find_meeting_times.find_meeting_times_post_request_body import FindMeetingTimesPostRequestBody
from msgraph.generated.users.item.assign_license.assign_license_post_request_body import AssignLicensePostRequestBody
from msgraph.generated.models.assigned_license import AssignedLicense

from schemas.entities import users as user_schemas


if TYPE_CHECKING:
    from services.time import TimeService
    from core.config import Config


logger = logging.getLogger(__name__)


class GraphService:
    def __init__(self, config: Config, time_service: TimeService):
        self._time_service = time_service
        
        self._domain = config.GRAPH_DOMAIN
        self._default_license_sku_id = config.DEFAULT_LICENSE_SKU_ID
        
        self._credentials = ClientSecretCredential(
            tenant_id=config.TENANT_ID,
            client_id=config.APP_ID,
            client_secret=config.APP_PASSWORD
        )   
        
        self._client = GraphServiceClient(credentials=self._credentials)
        
    async def close(self):
        await self._credentials.close()
        

    def _create_date_time_timezone(
        self,
        dt: datetime,
    ) -> DateTimeTimeZone:
        iso_str = dt.isoformat() if dt.tzinfo else f"{dt.isoformat()}Z"
        return DateTimeTimeZone(date_time=iso_str, time_zone="UTC")
        
    def _map_to_attendee(self, email: str) -> Attendee:
        return Attendee(
            email_address=EmailAddress(address=email),
            type="required"
        )
        
    def _prepare_user_data(
        self,
        request: user_schemas.UserCreateRequest
    ) -> user_schemas.UserProvisioningData:
        raw_nickname = request.effective_nickname_source
        nickname = transliterate_for_azure(raw_nickname)
        if not nickname:
            nickname = "user" + str(int(self._time_service.timestamp()))
            
        upn = f"{nickname}@{self._domain}"
        password = generate_strong_password()
        
        return user_schemas.UserProvisioningData(
            nickname=nickname,
            upn=upn,
            password=password
        )
        
        
    async def create_user(
        self, 
        request: user_schemas.UserCreateRequest 
        ) -> ServiceResponse[user_schemas.UserResponse]:
        prep_data = self._prepare_user_data(request)
        
        new_user = User(
            account_enabled=True,
            display_name=f"{request.first_name} {request.last_name}",
            mail_nickname=prep_data.nickname,
            user_principal_name=prep_data.upn,
            password_profile=PasswordProfile(
                force_change_password_next_sign_in=True,
                password=prep_data.password
            ),
            usage_location=request.usage_location,
            job_title=request.job_title,
            department=request.department
        )
        
        try:
            created_user = await self._client.users.post(new_user)
            license_assigned = False
            license_error = None
            
            if self._default_license_sku_id:
                lic_res = await self.assign_license_to_user(created_user.id, self._default_license_sku_id)
                license_assigned = lic_res.success
                if not lic_res.success:
                    license_error = lic_res.error
            
            user_response = user_schemas.UserResponse(
                userId=created_user.id,
                email=created_user.user_principal_name,
                password=prep_data.password,
                licenseAssigned=license_assigned,
                licenseError=license_error
            )
            return ServiceResponse.ok(user_response)
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            return ServiceResponse.fail(str(e))
        
    async def search_users(
        self, 
        search_term: str, 
        limit: int = 10
        ) -> ServiceResponse[List[user_schemas.UserSearchResult]]:
        candidates = [search_term]
        if is_cyrillic(search_term):
            transliterated = transliterate_for_azure(search_term)
            if transliterated and transliterated != search_term:
                candidates.append(transliterated)
        
        filter_clauses = []
        for term in candidates:
            safe_term = term.replace("'", "''")
            filter_clauses.append(f"startswith(displayName,'{safe_term}')")
            filter_clauses.append(f"startswith(mail,'{safe_term}')")
            filter_clauses.append(f"startswith(userPrincipalName,'{safe_term}')")
        
        filter_query = " or ".join(filter_clauses)
        
        try:
            query_params = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
                filter=filter_query,
                top=limit,
                select=[
                    "id", 
                    "displayName", 
                    "mail", 
                    "userPrincipalName",
                    "jobTitle",
                    "department"
                    ],
                orderby=["displayName"]
            )
            request_config = UsersRequestBuilder.UsersRequestBuilderGetRequestConfiguration(
                query_parameters=query_params
            )
            users_response = await self._client.users.get(request_configuration=request_config)
            users_list = []
            if users_response and users_response.value:
                for u in users_response.value:
                    users_list.append(
                        user_schemas.UserSearchResult(
                            user_id=u.id,
                            display_name=u.display_name,
                            email=u.mail,
                            upn=u.user_principal_name,
                            job_title=u.job_title,
                            department=u.department
                        )
                    )
            
            return ServiceResponse.ok(users_list)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return ServiceResponse.fail(str(e))
        
    async def assign_license_to_user(self, user_id: str, sku_id: str) -> ServiceResponse[bool]:
        try:
            request_body = AssignLicensePostRequestBody(
                add_licenses=[AssignedLicense(sku_id=sku_id)],
                remove_licenses=[]
            )
            await self._client.users.by_user_id(user_id).assign_license.post(request_body)
            return ServiceResponse.ok(True)
        except Exception as e:
            return ServiceResponse.fail(str(e))
                    
                    
    async def find_free_slots(
        self, 
        organizer_id: str, 
        user_emails: List[str], 
        start_date: datetime, 
        end_date: datetime, 
        duration_minutes: int = 30
    ) -> ServiceResponse[List[Dict]]:
        try:
            request_body = FindMeetingTimesPostRequestBody(
                attendees=[self._map_to_attendee(email) for email in user_emails],
                time_constraint=TimeConstraint(
                    timeslots=[TimeSlot(
                        start=self._create_datetime_timezone(start_date),
                        end=self._create_datetime_timezone(end_date)
                    )]
                ),
                meeting_duration=f"PT{duration_minutes}M",
                max_candidates=10,
                is_organizer_optional=False
            )
            result = await self._client.users.by_user_id(organizer_id).find_meeting_times.post(request_body)
            suggestions = []
            if result and result.meeting_time_suggestions:
                for slot in result.meeting_time_suggestions:
                    if slot.meeting_time_slot and slot.meeting_time_slot.start:
                        suggestions.append({
                            "start": slot.meeting_time_slot.start.date_time,
                            "end": slot.meeting_time_slot.end.date_time,
                        })
            
            return ServiceResponse.ok(suggestions)    
        except Exception as e:
            logger.error(f"Find meeting times failed: {e}")
            return ServiceResponse.fail(str(e))
        
    async def create_meeting(
        self, 
        organizer_id: str, 
        attendees: List[str], 
        subject: str, 
        start_time: datetime, 
        end_time: datetime, 
        body: str = "",
        agenda: Optional[str] = None
    ) -> ServiceResponse[Dict]:
        content_html = body or "<p>Meeting scheduled by HR Bot</p>"
        if agenda:
            content_html += f"<br/><h3>Agenda:</h3><p>{agenda.replace(chr(10), '<br>')}</p>"

        try:
            request_body = Event(
                subject=subject,
                body=ItemBody(
                    content_type=BodyType.Html,
                    content=content_html
                ),
                start=self._create_datetime_timezone(start_time),
                end=self._create_datetime_timezone(end_time),
                attendees=[self._map_to_attendee(email) for email in attendees],
                is_online_meeting=True,
                online_meeting_provider=OnlineMeetingProviderType.TeamsForBusiness
            )
            created_event = await self.client.users.by_user_id(organizer_id).events.post(request_body)
            return ServiceResponse.ok({
                "id": created_event.id,
                "webLink": created_event.web_link,
                "joinUrl": created_event.online_meeting.join_url if created_event.online_meeting else None
            })

        except Exception as e:
            return ServiceResponse.fail(str(e))
    
    
__all__ = (
    "GraphService",
)

