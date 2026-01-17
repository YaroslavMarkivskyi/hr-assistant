from enum import StrEnum


class GeneralAction(StrEnum):
    """General actions (Navigation, Help, Settings)"""
    OPEN_MAIN_MENU = "open_main_menu"
    GO_BACK = "go_back"
    CANCEL_OPERATION = "cancel_operation"
    Provide_Feedback = "provide_feedback"
    

__all__ = ("GeneralAction",)

