import numpy as np

from .base import BaseModelService
from ..baml_client.types import TitanicInput


class TitanicModelService(BaseModelService):
    model_name = "titanic"

    def __init__(self):
        super().__init__()
        self.map = {
            "SexTypes": {
                "MALE": "male",
                "FEMALE": "female",
            },
            "ClassTypes": {
                "FIRST": 1,
                "SECOND": 2,
                "THIRD": 3,
            },
            "EmbarkTypes": {
                "ENGLAND": "S",
                "FRANCE": "C",
                "IRELAND": "Q",
            },
            "AloneTypes": {
                "TRUE": 1,
                "FALSE": 0,
            },
        }

    def transform(self, inp: TitanicInput):
        sex_val = self.map["SexTypes"][inp.sex.name]
        pclass_val = self.map["ClassTypes"][inp.pclass.name]
        embarked_val = self.map["EmbarkTypes"][inp.embarked.name]
        alone_val = self.map["AloneTypes"][inp.alone.name]

        features = {
            "sex": sex_val,
            "pclass": pclass_val,
            "embarked": embarked_val,
            "alone": alone_val,
        }
        return features

    def valid_values(self):
        return {k: list(v.keys()) for k, v in self.map.items()}

    def build_feed(self, features):
        return {
            "sex": np.array([[features["sex"]]], dtype=object),
            "pclass": np.array([[features["pclass"]]], dtype=np.int64),
            "embarked": np.array([[features["embarked"]]], dtype=object),
            "alone": np.array([[features["alone"]]], dtype=np.int64),
        }

    def format_response(self, raw_pred):
        pred = raw_pred["prediction"]
        label = "didnt make it" if pred == 0 else "survived"
        return f"you probably {label}"
