"""
User Search Service - main orchestrator for user search and resolution.

This service coordinates the search process using:
- GraphService for API calls
- FuzzyMatcher for quick disambiguation
- LRUCache for performance
- AIService for complex disambiguation
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple, TYPE_CHECKING

from .types import UserDict, ConfidenceLevel
from .cache import LRUCache
from .fuzzy_matcher import FuzzyMatcher

if TYPE_CHECKING:
    from services.graph_service import GraphService
    from interfaces.ai_service import AIService

logger = logging.getLogger("HRBot")


class UserSearchService:
    """
    Service for searching and resolving users by name.
    
    Handles:
    - Exact name matching
    - Advanced fallback search with Graph API $filter
    - Fuzzy matching for quick disambiguation (before AI)
    - AI-powered best match selection
    - Ambiguous user selection via Adaptive Cards
    - Self-reference handling ("me", "я", etc.)
    - LRU caching for performance
    """
    
    def __init__(
        self,
        graph_service: "GraphService",
        ai_service: Optional["AIService"] = None,
        enable_cache: bool = True
    ):
        """
        Initialize UserSearchService.
        
        Args:
            graph_service: Service for Microsoft Graph API calls
            ai_service: Optional AI service for best match selection
            enable_cache: Whether to enable LRU cache for search results
        """
        self.graph_service = graph_service
        self.ai_service = ai_service
        self.cache = LRUCache() if enable_cache else None
        self.fuzzy_matcher = FuzzyMatcher()
    
    async def resolve_users(
        self,
        participants: List[Dict[str, Any]],
        requester_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Resolves user names and finds their IDs.
        
        This is the main entry point for user resolution. It handles:
        - Self-references ("me", "я", "мене")
        - Exact name matching
        - Fallback search strategies
        - Fuzzy matching for quick disambiguation
        - AI-powered disambiguation
        - Ambiguous result handling
        
        Performance: Resolves all participants in parallel using asyncio.gather
        for faster execution when multiple users need to be found.
        
        Args:
            participants: List of participant dicts with 'name' and optional 'type'
            requester_id: Azure AD Object ID of the requester (for "self" resolution)
            
        Returns:
            Dict with:
            - success: bool - whether all users were resolved
            - users: List[Dict] - resolved users (if success=True)
            - ambiguous: bool - whether user selection is needed (if success=False)
            - selections: List[Dict] - ambiguous selections for Adaptive Cards
            - error: str - error message (if success=False and not ambiguous)
        """
        # Separate self-references from regular searches
        # We need to track names for ambiguous results
        self_refs = []
        search_tasks = []
        search_names = []  # Track names for ambiguous result handling
        
        for participant in participants:
            name = participant.get('name', '').strip()
            p_type = participant.get('type', 'name')
            
            # Handle self-reference (must be done sequentially as it depends on requester_id)
            if p_type == "self" or name.lower() in ["me", "я", "мене", "мною"]:
                self_refs.append(participant)
            else:
                # Regular search - add to parallel tasks
                search_tasks.append(self._search_and_resolve_user(name))
                search_names.append(name)  # Track name for this search
        
        # Resolve self-references first (if any)
        resolved_users: List[UserDict] = []
        if self_refs and requester_id:
            user_result = await self.graph_service.get_user_by_id(requester_id)
            if user_result.get("success"):
                resolved_users.append({
                    "id": requester_id,
                    "displayName": user_result["user"].get("displayName"),
                    "mail": user_result["user"].get("mail"),
                    "userPrincipalName": user_result["user"].get("userPrincipalName")
                })
        
        # Resolve all regular searches in parallel
        if search_tasks:
            results = await asyncio.gather(*search_tasks, return_exceptions=True)
        else:
            results = []
        
        # Process results
        ambiguous_selections = []
        
        for idx, result in enumerate(results):
            # Handle exceptions from parallel execution
            if isinstance(result, Exception):
                logger.error(f"❌ Error resolving user: {result}", exc_info=result)
                return {
                    "success": False,
                    "error": f"Помилка пошуку користувача: {str(result)}"
                }
            
            # Get the corresponding search name
            search_name = search_names[idx] if idx < len(search_names) else ""
            
            if result.get("success"):
                # User resolved successfully
                resolved_users.append(result["user"])
            elif result.get("ambiguous"):
                # Ambiguous result - need user selection
                ambiguous_selections.append({
                    "search_term": search_name,
                    "users": result.get("users", [])
                })
            else:
                # Error - user not found
                error_msg = result.get("error", f"Користувача '{search_name}' не знайдено")
                return {
                    "success": False,
                    "error": error_msg
                }
        
        # Check if we have ambiguous selections
        if ambiguous_selections:
            return {
                "success": False,
                "ambiguous": True,
                "selections": ambiguous_selections,
                "resolved": resolved_users
            }
        
        return {"success": True, "users": resolved_users}
    
    async def search_user(
        self,
        name: str,
        use_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Search for a single user by name.
        
        Args:
            name: User name to search for
            use_ai: Whether to use AI for disambiguation if multiple results
            
        Returns:
            Dict with:
            - success: bool
            - user: Dict - user data (if success=True and unambiguous)
            - users: List[Dict] - multiple users (if ambiguous)
            - ambiguous: bool - whether selection is needed
            - error: str - error message (if success=False)
        """
        result = await self._search_and_resolve_user(name, use_ai)
        # Add search_term for consistency with resolve_users
        if not result.get("success") and result.get("ambiguous"):
            result["search_term"] = name
        return result
    
    async def _search_and_resolve_user(
        self,
        name: str,
        use_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Internal method to search and resolve a single user.
        
        Strategy:
        1. Check cache
        2. Try exact search via Graph API
        3. Check for exact match (full name, single result)
        4. If no results, try improved fallback search (advanced Graph API query)
        5. If multiple results, try fuzzy matching (fast, before AI)
        6. If still ambiguous, use AI to select best match (if available)
        7. Cache result and return
        
        Args:
            name: User name to search for
            use_ai: Whether to use AI for disambiguation
            
        Returns:
            Dict with resolution result
        """
        # Check cache first
        cache_key = self._get_cache_key(name)
        cached_result = self._get_cached_result(cache_key, name)
        if cached_result:
            return cached_result
        
        # Step 1: Try exact search
        users, exact_match_found = await self._try_exact_search(name)
        
        # Step 2: Fallback search if no results
        if len(users) == 0:
            fallback_result = await self._try_fallback_search(name, cache_key, use_ai)
            if fallback_result:
                # Fallback search already resolved (cached and returned)
                return fallback_result
            # If fallback returned None, continue with empty users list
        
        # Step 3: Process and resolve results
        return await self._resolve_search_results(cache_key, name, users, exact_match_found, use_ai)
    
    async def _try_exact_search(self, name: str) -> Tuple[List[UserDict], bool]:
        """
        Try exact search via Graph API.
        
        Returns:
            Tuple of (users list, exact_match_found bool)
        """
        search_result = await self.graph_service.search_users(name, limit=5)
        
        users: List[UserDict] = []
        exact_match_found = False
        
        if search_result.get("success"):
            users = search_result.get("users", [])
            
            # Check for exact match (full name, single result)
            if len(name.split()) >= 2 and len(users) == 1:
                user_display_name = users[0].get('displayName', '').lower()
                name_lower = name.lower()
                name_parts = name_lower.split()
                
                # If all name parts are in displayName - it's an exact match
                if all(part in user_display_name for part in name_parts):
                    exact_match_found = True
                    logger.info(f"✅ Exact match found: {users[0].get('displayName')}")
        
        return users, exact_match_found
    
    async def _try_fallback_search(
        self, 
        name: str, 
        cache_key: str, 
        use_ai: bool
    ) -> Optional[Dict[str, Any]]:
        """
        Try improved fallback search if exact search found no results.
        
        Handles different scenarios:
        - 0 users: return error
        - 1 user: return success
        - 2-10 users: try fuzzy matching, then ambiguous if needed
        - >10 users: try fuzzy matching, then AI, then ambiguous
        
        Returns:
            Dict with resolution result if resolved, None if should continue with empty users
        """
        logger.info(f"⚠️ Exact search found no results for '{name}', trying improved fallback...")
        fallback_result = await self._improved_fallback_search(name)
        
        if not fallback_result.get("success"):
            return self._cache_and_return(cache_key, {"success": False, "error": f"Користувача '{name}' не знайдено"})
        
        fallback_users = fallback_result.get("users", [])
        logger.info(f"📋 Found {len(fallback_users)} users via improved fallback search")
        
        if len(fallback_users) == 0:
            return self._cache_and_return(cache_key, {"success": False, "error": f"Користувача '{name}' не знайдено"})
        elif len(fallback_users) == 1:
            # Single result - use it
            return self._cache_and_return(cache_key, {"success": True, "user": fallback_users[0]})
        elif len(fallback_users) <= 10:
            # 2-10 users - try fuzzy matching first
            fuzzy_result = self.fuzzy_matcher.find_best_match(name, fallback_users)
            if fuzzy_result:
                return self._cache_and_return(cache_key, {"success": True, "user": fuzzy_result})
            
            # No good fuzzy match - mark as ambiguous
            return self._cache_and_return(cache_key, {
                "success": False,
                "ambiguous": True,
                "users": fallback_users
            })
        else:
            # Many users - try fuzzy matching first, then AI
            fuzzy_result = self.fuzzy_matcher.find_best_match(name, fallback_users)
            if fuzzy_result:
                return self._cache_and_return(cache_key, {"success": True, "user": fuzzy_result})
            
            # Try AI selection if available
            ai_result = await self._try_ai_selection(name, fallback_users[:20], use_ai)
            if ai_result:
                return self._cache_and_return(cache_key, ai_result)
            
            # No AI or AI failed - show first 10
            return self._cache_and_return(cache_key, {
                "success": False,
                "ambiguous": True,
                "users": fallback_users[:10]
            })
    
    async def _resolve_search_results(
        self,
        cache_key: str,
        name: str,
        users: List[UserDict],
        exact_match_found: bool,
        use_ai: bool
    ) -> Dict[str, Any]:
        """
        Resolve search results using fuzzy matching and AI.
        
        This method handles the resolution logic for different result scenarios:
        - Exact match found
        - Single user found
        - Multiple users found (fuzzy matching -> AI -> ambiguous)
        - No users found
        
        Returns:
            Dict with resolution result
        """
        # Exact match - use it immediately
        if exact_match_found:
            return self._cache_and_return(cache_key, {"success": True, "user": users[0]})
        
        # No users found
        if len(users) == 0:
            return self._cache_and_return(cache_key, {"success": False, "error": f"Користувача '{name}' не знайдено"})
        
        # Single user found
        if len(users) == 1:
            return self._cache_and_return(cache_key, {"success": True, "user": users[0]})
        
        # Multiple users - try fuzzy matching first (fast!)
        fuzzy_result = self.fuzzy_matcher.find_best_match(name, users)
        if fuzzy_result:
            return self._cache_and_return(cache_key, {"success": True, "user": fuzzy_result})
        
        # No good fuzzy match - try AI disambiguation
        if len(users) <= 5:
            ai_result = await self._try_ai_selection(name, users, use_ai)
            if ai_result:
                return self._cache_and_return(cache_key, ai_result)
        
        # Many users or no AI - show selection card
        return self._cache_and_return(cache_key, {
            "success": False,
            "ambiguous": True,
            "users": users[:10] if len(users) > 10 else users
        })
    
    async def _improved_fallback_search(self, name: str) -> Dict[str, Any]:
        """
        Improved fallback search using advanced Graph API queries.
        
        Instead of searching by first letter only, uses:
        - Minimum 3 characters for startsWith filter
        - Searches in displayName, givenName, surname, mail
        - More precise than first-letter-only search
        
        Uses GraphService.execute_custom_query() to maintain proper architecture.
        
        Args:
            name: User name to search for
            
        Returns:
            Dict with search results
        """
        # Extract name parts
        parts = name.strip().split()
        if len(parts) == 0:
            return {"success": False, "error": "Empty search term"}
        
        # Use first name or last name (whichever is longer, minimum 3 chars)
        search_term = max(parts, key=len)
        
        # Minimum 3 characters for startsWith filter
        if len(search_term) < 3:
            # If too short, fall back to old method
            return await self.graph_service.search_users_by_first_letter(name, limit=20)
        
        # Use Graph API advanced query via GraphService's public method
        # Search in multiple fields: displayName, givenName, surname, mail
        try:
            # Build $filter query (using endpoint + params, not hardcoded URL)
            filter_query = (
                f"startswith(displayName,'{search_term}') or "
                f"startswith(givenName,'{search_term}') or "
                f"startswith(surname,'{search_term}') or "
                f"startswith(mail,'{search_term}')"
            )
            
            # Use GraphService's public method with proper endpoint and ConsistencyLevel
            # ConsistencyLevel: eventual is required for complex OR queries across fields
            query_result = await self.graph_service.execute_custom_query(
                endpoint="users",
                params={
                    "$filter": filter_query,
                    "$top": "20",
                    "$orderby": "displayName",
                    "$select": "id,displayName,mail,userPrincipalName,givenName,surname"
                },
                use_consistency_level=True  # Required for OR queries across multiple fields
            )
            
            if query_result.get("success"):
                data = query_result.get("data", {})
                users = data.get('value', [])
                logger.info(f"📊 Advanced fallback found {len(users)} users for '{search_term}'")
                return {"success": True, "users": users}
            else:
                error_msg = query_result.get("error", "Unknown error")
                logger.warning(f"⚠️ Advanced fallback search failed: {error_msg}")
                # Fall back to old method
                return await self.graph_service.search_users_by_first_letter(name, limit=20)
        except Exception as e:
            logger.warning(f"⚠️ Advanced fallback search error: {e}, falling back to first-letter search")
            # Fall back to old method
            return await self.graph_service.search_users_by_first_letter(name, limit=20)
    
    def _get_cache_key(self, name: str) -> str:
        """Generate cache key for a search term"""
        return f"search:{name.lower().strip()}"
    
    def _get_cached_result(self, cache_key: str, name: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available"""
        if self.cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.debug(f"💾 Cache hit for '{name}'")
                return cached_result
        return None
    
    def _cache_and_return(self, cache_key: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Cache result and return it"""
        if self.cache:
            self.cache.set(cache_key, result)
        return result
    
    async def _try_ai_selection(
        self,
        search_term: str,
        users: List[UserDict],
        use_ai: bool
    ) -> Optional[Dict[str, Any]]:
        """
        Helper method to try AI-powered user selection.
        
        This method encapsulates the AI selection logic to avoid duplication.
        Used in both fallback and normal search paths.
        
        Args:
            search_term: The original search query
            users: List of candidate users to choose from
            use_ai: Whether to use AI (if False, returns None immediately)
            
        Returns:
            Dict with resolution result if AI successfully selected a user,
            None if AI should not be used or failed to select.
        """
        if not use_ai or not self.ai_service:
            return None
        
        logger.info(f"🤖 Using AI to select best match from {len(users)} users for '{search_term}'...")
        
        try:
            ai_result = await self.ai_service.select_best_user_match(search_term, users)
            
            if not ai_result.get("success"):
                logger.debug(f"⚠️ AI could not select a user for '{search_term}'")
                return None
            
            selected_user = ai_result.get("user")
            confidence: ConfidenceLevel = ai_result.get("confidence", "medium")
            logger.info(f"✅ AI selected: {selected_user.get('displayName')} (confidence: {confidence})")
            
            # Only auto-select if confidence is high
            if confidence == "high":
                return {"success": True, "user": selected_user}
            else:
                # Medium/low confidence - return None to trigger selection card
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ AI selection failed for '{search_term}': {e}")
            return None


