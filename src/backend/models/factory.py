from dataclasses import dataclass

from ..baml_client import b
from .titanic import TitanicModelService
# from .insurance import InsuranceModelService


class ModelFactory:
    registry = {
        "titanic": TitanicModelService,
        # "insurance": InsuranceModelService,
    }

    @classmethod
    def create(cls, model_name):
        service_cls = cls.registry[model_name]
        return service_cls()
