"""
Fuzzy matching logic for user search.

This module handles string similarity matching using rapidfuzz (if available)
or a simple fallback implementation.
"""
import logging
from typing import List, Optional, Tuple

from .types import UserDict

logger = logging.getLogger("HRBot")

# Try to import rapidfuzz for fuzzy matching, fallback to simple matching if not available
try:
    from rapidfuzz import fuzz
    HAS_FUZZY = True
except ImportError:
    HAS_FUZZY = False
    logger.warning("⚠️ rapidfuzz not installed. Install with: pip install rapidfuzz")
    
    # Simple fallback fuzzy matching
    def _simple_fuzzy_ratio(str1: str, str2: str) -> float:
        """Simple fuzzy matching fallback"""
        str1_lower = str1.lower()
        str2_lower = str2.lower()
        if str1_lower == str2_lower:
            return 100.0
        if str1_lower in str2_lower or str2_lower in str1_lower:
            return 85.0
        return 0.0


class FuzzyMatcher:
    """
    Fuzzy matching service for finding best user matches.
    
    This is much faster than AI (0.001s vs 2-4s) and often gives the same result
    for obvious matches like "Yaroslav" vs ["Yaroslav A", "Yaroslav B"].
    """
    
    @staticmethod
    def find_best_match(
        search_term: str,
        users: List[UserDict],
        threshold: float = 90.0,
        margin_of_victory: float = 5.0
    ) -> Optional[UserDict]:
        """
        Try fuzzy matching to quickly find the best match before using AI.
        
        Safety: Checks "margin of victory" - if two users have similar high scores,
        returns None to trigger ambiguous selection (prevents wrong user assignment).
        
        Args:
            search_term: The search query
            users: List of candidate users
            threshold: Minimum similarity score (0-100) to auto-select
            margin_of_victory: Minimum score difference between 1st and 2nd place (default: 5.0)
            
        Returns:
            Best matching user if score >= threshold AND margin is sufficient, None otherwise
        """
        if not users:
            return None
        
        # If only one user, return it (no need for fuzzy matching)
        if len(users) == 1:
            return users[0]
        
        # Calculate scores for all users
        user_scores: List[Tuple[UserDict, float]] = []
        search_term_lower = search_term.lower()
        
        for user in users:
            # Try matching against displayName, givenName, surname
            display_name = user.get('displayName', '').lower()
            given_name = user.get('givenName', '').lower()
            surname = user.get('surname', '').lower()
            
            # Calculate similarity scores
            if HAS_FUZZY:
                scores = [
                    fuzz.ratio(search_term_lower, display_name),
                    fuzz.ratio(search_term_lower, given_name) if given_name else 0,
                    fuzz.ratio(search_term_lower, surname) if surname else 0,
                    fuzz.partial_ratio(search_term_lower, display_name),  # Partial match
                ]
            else:
                # Fallback to simple matching
                scores = [
                    _simple_fuzzy_ratio(search_term_lower, display_name),
                    _simple_fuzzy_ratio(search_term_lower, given_name) if given_name else 0,
                    _simple_fuzzy_ratio(search_term_lower, surname) if surname else 0,
                ]
            
            max_score = max(scores)
            user_scores.append((user, max_score))
        
        # Sort by score (descending)
        user_scores.sort(key=lambda x: x[1], reverse=True)
        
        best_user, best_score = user_scores[0]
        
        # Check if score meets threshold
        if best_score < threshold:
            logger.debug(f"⚠️ Fuzzy matching: best score {best_score:.1f}% < threshold {threshold}%")
            return None
        
        # Check margin of victory (safety check)
        if len(user_scores) > 1:
            second_score = user_scores[1][1]
            score_gap = best_score - second_score
            
            if score_gap < margin_of_victory:
                logger.warning(
                    f"⚠️ Fuzzy matching: ambiguous results - "
                    f"best: {best_user.get('displayName')} ({best_score:.1f}%), "
                    f"second: {user_scores[1][0].get('displayName')} ({second_score:.1f}%), "
                    f"gap: {score_gap:.1f}% < {margin_of_victory}%"
                )
                return None  # Too close - trigger ambiguous selection
        
        logger.info(f"🎯 Fuzzy match found: {best_user.get('displayName')} (score: {best_score:.1f}%)")
        return best_user


