from .titanic import TitanicModelService
# from .insurance import InsuranceModelService
from ..baml_client import b

MODEL_SERVICES = {
    "titanic": {
        "service_cls": TitanicModelService,
        "validate_fn": b.TitanicValidateInput,
    },
    # "insurance_premium": {
    #     "service_cls": InsuranceModelService,
    #     "validate_fn": b.InsuranceValidateInput,
    # },
}

