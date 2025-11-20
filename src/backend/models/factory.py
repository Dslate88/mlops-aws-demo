from ..baml_client import b
from .titanic import TitanicModelService
# from .insurance import InsuranceModelService


class ModelFactory:
    registry = {
        "titanic": {
            "service_cls": TitanicModelService,
            "validate_fn": b.TitanicValidateInput,
        },
        # "insurance_premium": {
        #     "service_cls": InsuranceModelService,
        #     "validate_fn": b.InsuranceValidateInput,
        # },
    }

    @classmethod
    def create(cls, model_name):
        entry = cls.registry[model_name]
        return entry["service_cls"](), entry["validate_fn"]
