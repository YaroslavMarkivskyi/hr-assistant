"""
Bot modules - main functional blocks

This file contains only module definitions. It rarely changes.
"""
from enum import StrEnum


class BotModule(StrEnum):
    """
    Bot modules - main functional blocks of the bot
    
    Currently only SCHEDULING is implemented.
    Other modules will be added in the future.
    """
    SCHEDULING = "scheduling"  # Smart scheduling with availability, booking, CRUD, workshops, daily briefing
    GENERAL = "general"        # General Q&A, FAQs, company policies, knowledge base

