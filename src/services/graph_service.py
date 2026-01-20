from __future__ import annotations
import logging

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, TYPE_CHECKING

from http import HTTPStatus

import httpx

from core.utils.security_utils import generate_strong_password
from core.utils.text_utils import is_cyrillic, transliterate_for_azure
from schemas.service_response import ServiceResponse

if TYPE_CHECKING:
    from services.time import TimeService
    from core.config import Config


logger = logging.getLogger(__name__)


class GraphService:
    BASE_URL = "https://graph.microsoft.com/v1.0"
    AUTH_URL_TEMPLATE = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    
    def __init__(self, config: Config, time_service: TimeService):
        self._time_service = time_service
        self._client_id = config.APP_ID
        self._client_secret = config.APP_PASSWORD
        self._tenant_id = config.TENANT_ID or "common" # TODO: warn if not set
        
        self._domain = config.GRAPH_DOMAIN
        self._default_license_sku_id = config.DEFAULT_LICENSE_SKU_ID
        
        
        self._client = httpx.AsyncClient(
            base_url=config.GRAPH_API_BASE_URL,
            timeout=30.0
        )
        
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        
    async def close(self):
        await self._client.aclose()
        
    async def _get_token(self) -> str:
        now = self._time_service.now_utc() 
        
        if (
            self._access_token
            and self._token_expires_at
            and self._token_expires_at > (now + timedelta(minutes=5))
        ):
            return self._access_token
        logger.info(" Refreshing Microsoft Graph access token...")
        url = self.AUTH_URL_TEMPLATE.format(tenant_id=self._tenant_id)
        
        payload = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials"
        }
        
        async with httpx.AsyncClient() as auth_client:
            try:
                resp = await auth_client.post(url, data=payload)
                resp.raise_for_status()
                
                data = resp.json()
                self._access_token = data["access_token"]
                
                expires_in_seconds = int(data.get("expires_in", 3600))
                self._token_expires_at = now + timedelta(seconds=expires_in_seconds)
                
                return self._access_token
            except httpx.HTTPError as e:
                logger.error(f"Failed to obtain access token: {e}")
                raise ConnectionError(f"Failed to authenticate with Microsoft Graph: {e}")

    async def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> ServiceResponse[Any]:
        try:
            token = await self._get_token()
            
            request_headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            if headers:
                request_headers.update(headers)
                
            response = await self._client.request(
                method=method,
                url=endpoint,
                json=json_data,
                params=params,
                headers=request_headers,
            )
            
            if response.is_success:
                if response.status_code == HTTPStatus.NO_CONTENT:
                    return ServiceResponse.ok(None, status_code=HTTPStatus.NO_CONTENT)
                return ServiceResponse.ok(response.json(), status_code=response.status_code)
            
            try:
                error_body = response.json()
                error_data = error_body.get('error', {})
                if isinstance(error_data, dict):
                    error_msg = f"{error_data.get('code', 'Error')}: {error_data.get('message', 'Unknown')}"
                else:
                    error_msg = str(error_data)
            except Exception:
                error_msg = response.text
            logger.warning(f"Graph API Error [{method} {endpoint}]: {response.status_code} - {error_msg}")
            return ServiceResponse.fail(error_msg, status_code=response.status_code)
        except httpx.TimeoutException:
            logger.error(f"Timeout connecting to Microsoft Graph [{endpoint}]")
            return ServiceResponse.fail("Request timeout", status_code=HTTPStatus.GATEWAY_TIMEOUT)
        except Exception as e:
            logger.error(f"System Error in GraphService: {e}", exc_info=True)
            return ServiceResponse.fail(str(e))
        
    async def create_user(
        self,
        data: Dict[str, Any],
    ) -> ServiceResponse[Dict[str, Any]]:
        first_name = data.get('firstName', '')
        last_name = data.get('lastName', '')
        
        raw_nickname = data.get('emailNickname') or last_name
        nickname = transliterate_for_azure(raw_nickname)
        
        if not nickname:
            nickname = "user" + str(int(self._time_service.timestamp()))
            
        upn = f"{nickname}@{self.domain}"
        password = generate_strong_password()
        
        user_payload = {
            "accountEnabled": True,
            "displayName": f"{first_name} {last_name}",
            "mailNickname": nickname,
            "userPrincipalName": upn,
            "passwordProfile": {
                "forceChangePasswordNextSignIn": True,
                "password": password
            },
            "jobTitle": data.get('jobTitle'),
            "department": data.get('department'),
            "usageLocation": "US"
        }
        
        logger.info(f"Creating user request for: {upn}")
        
        create_res = await self._request("POST", "/users", json_data=user_payload)
        
        if not create_res.success:
            return create_res
        
        user_id = create_res.data.get("id")
        result_data = {
            "user_id": user_id,
            "email": upn,
            "password": password,
            "license_assigned": False
        }
        
        if self.default_license_sku:
            logger.info(f"Assigning license {self.default_license_sku} to {user_id}")
            lic_res = await self.assign_license_to_user(user_id, self.default_license_sku)
            if lic_res.success:
                result_data["license_assigned"] = True
            else:
                result_data["license_error"] = lic_res.error
        
        return ServiceResponse.ok(result_data, status_code=HTTPStatus.CREATED)
    
    async def search_users(
        self, 
        search_term: str, 
        limit: int = 10
        ) -> ServiceResponse[List[Dict]]:
        
        candidates = [search_term]
        
        if is_cyrillic(search_term):
            transliterated = transliterate_for_azure(search_term)
            if transliterated and transliterated != search_term:
                candidates.append(transliterated)
                logger.info(f"Adding transliterated search term: {transliterated}")
        
        search_clauses = []
        for term in candidates:
            clean = term.replace('"', '').replace("'", "")
            search_clauses.append(f'"displayName:{clean}"')
            search_clauses.append(f'"mail:{clean}"')
            
        params = {
            "$search": " OR ".join(search_clauses),
            "$top": limit,
            "$select": "id,displayName,mail,userPrincipalName,givenName,surname"
        }
        headers = {"ConsistencyLevel": "eventual"}
        
        res = await self._request("GET", "/users", params=params, headers=headers)
        
        if res.success and res.data.get("value"):
            return ServiceResponse.ok(res.data["value"])
        
        logger.info("Fallback to $filter search")
        
        filter_clauses = []
        for term in candidates:
            safe_term = term.replace("'", "''")
            filter_clauses.append(f"startswith(displayName,'{safe_term}')")
            filter_clauses.append(f"startswith(mail,'{safe_term}')")
            filter_clauses.append(f"startswith(userPrincipalName,'{safe_term}')")
        
        params = {
            "$filter": " or ".join(filter_clauses),
            "$top": limit,
            "$select": "id,displayName,mail,userPrincipalName"
        }
        
        res = await self._request("GET", "/users", params=params)
        
        if res.success:
            return ServiceResponse.ok(res.data.get("value", []))
            
        return res
    
    async def get_user_by_email(self, email: str) -> ServiceResponse[Dict]:
        return await self._request("GET", f"/users/{email}")
    
    async def get_user_by_id(self, user_id: str) -> ServiceResponse[Dict]:
        return await self._request("GET", f"/users/{user_id}")
    
    async def assign_license_to_user(self, user_id: str, sku_id: str) -> ServiceResponse[Dict]:
        payload = {
            "addLicenses": [{"skuId": sku_id}],
            "removeLicenses": []
        }
        return await self._request("POST", f"/users/{user_id}/assignLicense", json_data=payload)
    
    async def get_all_licenses(self) -> ServiceResponse[List[Dict]]:
        res = await self._request("GET", "/subscribedSkus")
        if res.success:
            return ServiceResponse.ok(res.data.get("value", []))
        return res
    
    async def search_groups(
        self, 
        search_term: str, 
        limit: int = 10
        ) -> ServiceResponse[List[Dict]]:
        safe_term = search_term.replace("'", "''")
        params = {
            "$filter": f"startswith(displayName,'{safe_term}') or startswith(mail,'{safe_term}')",
            "$top": str(limit),
            "$select": "id,displayName,mail,groupTypes,mailEnabled,securityEnabled"
        }
        res = await self._request("GET", "/groups", params=params)
        if res.success:
            return ServiceResponse.ok(res.data.get("value", []))
        return res
    
    async def get_group_members(self, group_id: str) -> ServiceResponse[List[Dict]]:
        params = {"$select": "id,displayName,mail,userPrincipalName"}
        res = await self._request("GET", f"/groups/{group_id}/members/microsoft.graph.user", params=params)
        if res.success:
            return ServiceResponse.ok(res.data.get("value", []))
        return res
    
    async def get_user_timezone(self, user_id: str) -> ServiceResponse[str]:
        res = await self._request("GET", f"/users/{user_id}/mailboxSettings")
        if res.success:
            tz = res.data.get('timeZone', 'UTC')
            return ServiceResponse.ok(tz)
        return ServiceResponse.ok('UTC')
    
    async def find_free_slots(
        self, 
        organizer_id: str, 
        user_emails: List[str], 
        start_date: datetime, 
        end_date: datetime, 
        duration_minutes: int = 30
    ) -> ServiceResponse[List[Dict]]:
        start_iso = start_date.isoformat() + "Z" if not start_date.tzinfo else start_date.isoformat()
        end_iso = end_date.isoformat() + "Z" if not end_date.tzinfo else end_date.isoformat()

        payload = {
            "attendees": [{"emailAddress": {"address": email}} for email in user_emails],
            "timeConstraint": {
                "timeslots": [{
                    "start": {"dateTime": start_iso, "timeZone": "UTC"},
                    "end": {"dateTime": end_iso, "timeZone": "UTC"}
                }]
            },
            "meetingDuration": f"PT{duration_minutes}M",
            "maxCandidates": 10,
            "isOrganizerOptional": False
        }
        res = await self._request("POST", f"/users/{organizer_id}/findMeetingTimes", json_data=payload)
        
        if res.success:
            return ServiceResponse.ok(res.data.get("meetingTimeSuggestions", []))
        return res
    
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
        
        content = body or "<p>Meeting scheduled by HR Bot</p>"
        if agenda:
            content += f"<br/><h3>Agenda:</h3><p>{agenda.replace(chr(10), '<br>')}</p>"

        payload = {
            "subject": subject,
            "body": {"contentType": "HTML", "content": content},
            "start": {"dateTime": start_time.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "UTC"},
            "attendees": [{"emailAddress": {"address": e}, "type": "required"} for e in attendees],
            "isOnlineMeeting": True,
            "onlineMeetingProvider": "teamsForBusiness"
        }
        headers = {"Prefer": 'outlook.timezone="UTC"'}
        
        return await self._request(
            "POST", 
            f"/users/{organizer_id}/calendar/events", 
            json_data=payload, 
            headers=headers
        )
    
    async def get_calendar_events(
        self, 
        user_id: str, 
        start_time: datetime, 
        end_time: datetime,
        include_details: bool = True
    ) -> ServiceResponse[List[Dict]]:
        
        select_fields = "id,subject,start,end,isAllDay,showAs,location,onlineMeeting"
        if not include_details:
            select_fields = "id,start,end,showAs"

        params = {
            "startDateTime": start_time.isoformat() + "Z" if not start_time.tzinfo else start_time.isoformat(),
            "endDateTime": end_time.isoformat() + "Z" if not end_time.tzinfo else end_time.isoformat(),
            "$select": select_fields,
            "$orderby": "start/dateTime",
            "$top": 50
        }
        
        res = await self._request("GET", f"/users/{user_id}/calendar/calendarView", params=params)
        
        if res.success:
            return ServiceResponse.ok(res.data.get("value", []))
        return res
    
    async def execute_custom_query(
        self, 
        endpoint: str, 
        params: Optional[Dict] = None,
        use_consistency_level: bool = False
    ) -> ServiceResponse[Any]:
        headers = {}
        if use_consistency_level:
            headers["ConsistencyLevel"] = "eventual"
            
        return await self._request("GET", endpoint, params=params, headers=headers)
    

__all__ = (
    "GraphService",
)

