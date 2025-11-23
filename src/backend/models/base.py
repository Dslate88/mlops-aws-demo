from abc import ABC, abstractmethod

import onnxruntime as rt
import mlflow


# TODO: check session thread once deployed..
class BaseModelService(ABC):
    model_name: str

    def __init__(self):
        self._session = None

    def get_session(self):
        if self._session is None:
            onnx_model = mlflow.onnx.load_model(f"models:/{self.model_name}/latest")
            self._session = rt.InferenceSession(onnx_model.SerializeToString())

        return self._session

    def predict(self, features):
        feed = self.build_feed(features)
        sess = self.get_session()
        output = sess.run(None, feed)
        pred = int(output[0].item())

        return {"prediction": pred}

    # TODO: bugfix needed...
    def missing_response(self, names):
        mapping = {
            # 0: "valid",
            1: "`{}` value is missing",
            2: "`{}` and `{}` are missing values",
            3: "`{}`, `{}` and `{}` are missing values",
            4: "`{}`, `{}`, `{}` and `{}` are missing values",
        }
        n = len(names)
        key = n if n < 4 else 4
        args = names if n < 5 else [names[0], names[1], n - 2]
        return mapping.get(key).format(*args)

    @abstractmethod
    def transform(self):
        pass

    # TODO: mv definition from titanic to this..
    @abstractmethod
    def valid_values(self):
        pass

    @abstractmethod
    def build_feed(self, features):
        pass

    @abstractmethod
    def format_response(self, raw_pred):
        pass

    @abstractmethod
    def train(self, config):
        pass
