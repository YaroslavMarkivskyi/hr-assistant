from core.base import BaseModule

from .controller import GeneralController


class GeneralModule(BaseModule):
    def __init__(self):
        super().__init__(controller=GeneralController())
        

__all__ = ("GeneralModule",)

