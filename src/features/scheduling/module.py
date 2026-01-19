from core.base import BaseModule

from features.scheduling.controller import SchedulingController


class SchedulingModule(BaseModule):
    def __init__(self):
        super().__init__(controller=SchedulingController())
    
    def setup(self):
        # Setup logic for SchedulingModule
        pass
    

__all__ = ("SchedulingModule",)