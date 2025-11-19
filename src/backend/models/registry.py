import mlflow
from mlflow.tracking import MlflowClient

MLFLOW_TRACKING_URI="http://127.0.0.1:5000/"
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("Default")

client = MlflowClient()

# TODO: maybe separate elevate/archive methods?
class ModelRegistry:
    def __init__(self, client):
        self.client = client
        self.models = self._get_models()
        
    def _latest_version(self, model_name):
        versions = self.client.search_model_versions(f"name='{model_name}'")
        return max([int(x.version) for x in versions])
    
    def _get_models(self):
        models = {}
        for rm in self.client.search_registered_models():
            latest = self._latest_version(rm.name)
            mv = self.client.get_model_version(rm.name, latest)
            models[rm.name] = mv.tags.get("app_stage")
        return models

    def _archive_models(self, tgt_model):
        for model, stage in mr.models.items():
            if stage == "Production" and model != tgt_model:
                client.set_model_version_tag(
                    name=model, version=self._latest_version(model), key="app_stage", value="Archived"
                )

    
    def set_model_stage(self, tgt_model, operation):
        version = self._latest_version(tgt_model)
        tgt_stage = "Production" if operation == "elevate" else "Archived"
        current_stage = client.get_model_version(tgt_model, version).tags.get("app_stage")

        # handle if valid elevate and need other model to be archived
        for model, stage in mr.models.items():
            if stage == "Production" and model != tgt_model:
                client.set_model_version_tag(
                    name=model, version=self._latest_version(model), key="app_stage", value="Archived"
                )

        # handle if app already in target state
        if current_stage != tgt_stage:
            client.set_model_version_tag(
                name=tgt_model, version=version, key="app_stage", value=tgt_stage
            )
            return f"`{tgt_model}` sucessfully set to `{tgt_stage}`."
        else:
            return f"No action taken. `{tgt_model}` already set to `{tgt_stage}`."


if __name__ == "__main__":
    mr = ModelRegistry(client)
    print("Before")
    print(mr.models)
    print("After")
    mr.set_model_stage("titanic", "elevate")
    # mr.set_model_stage("insurance_premium", "elevate")
    print(mr.models)
