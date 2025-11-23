import os
import mlflow
import mlflow.onnx
from mlflow.tracking import MlflowClient

import seaborn as sns
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from skl2onnx import to_onnx

import numpy as np

from .base import BaseModelService
from ..baml_client import b
from ..baml_client.types import TitanicInput, TitanicTrain

from .registry import ModelRegistry

client = MlflowClient()
mr = ModelRegistry(client)

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000/")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("Default")

class TitanicModelService(BaseModelService):
    val_inference = b.TitanicValidateInput
    val_train = b.TitanicValidateTrain

    def __init__(self):
        super().__init__()
        self.model_name = "titanic"
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

    def train(self, inp: TitanicTrain):
        with mlflow.start_run(run_name="titanic-logreg-onnx") as run:
            titanic = sns.load_dataset("titanic")
            
            y = titanic["survived"]
            X = titanic[["sex", "pclass", "embarked", "alone"]].copy()
            
            mask = X.notna().all(axis=1) & y.notna()
            X = X[mask]
            y = y[mask]
            
            X["pclass"] = X["pclass"].astype("category")
            X["alone"] = X["alone"].astype("int64")
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=inp.test_size, random_state=42, stratify=y
            )
            
            categorical_features = ["sex", "pclass", "embarked", "alone"]
            
            preprocess = ColumnTransformer(
                transformers=[
                    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
                ]
            )
            
            clf = Pipeline(
                steps=[
                    ("preprocess", preprocess),
                    ("model", LogisticRegression(max_iter=1000)),
                ]
            )
            
            clf.fit(X_train, y_train)
            
            y_pred = clf.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            mlflow.log_metric("accuracy", acc)
            mlflow.log_metric("x_train_size", len(X_train))
            mlflow.log_metric("x_test_size", len(X_test))
            mlflow.log_param("test_size", inp.test_size)
            
            example = pd.DataFrame(
                [
                    {
                        "sex": "female",
                        "pclass": 1,
                        "embarked": "S",
                        "alone": 0,
                    }
                ]
            )
            onnx_model = to_onnx(clf, X_train[:1])

            mlflow.onnx.log_model(
                onnx_model=onnx_model,
                name="model",
                registered_model_name=self.model_name,
            )

            return {
                    "accuracy": round(acc, 3),
                    "test_size": inp.test_size,
                    "x_train_rows": len(X_train),
                    "x_test_rows": len(X_test),
                    "model_name": self.model_name,
                    "run_id": run.info.run_id,
                    "experiment_id": run.info.experiment_id
                    }
