# import mlflow
# from mlflow.tracking import MlflowClient
#
# MLFLOW_TRACKING_URI="http://127.0.0.1:5000/"
# mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
# mlflow.set_experiment("Default")

# client = MlflowClient()

# TODO: methods that add to registry
class ModelRegistry:
    def __init__(self, client):
        self.client = client

    def __contains__(self, item):
        return item in self.list_models()

    def _latest_version(self, model_name):
        versions = self.client.search_model_versions(f"name='{model_name}'")
        return max([int(x.version) for x in versions])

    def _get_stage(self, model_name):
        version = self._latest_version(model_name)
        mv = self.client.get_model_version(model_name, version)
        return mv.tags.get("app_stage")

    def _set_stage(self, model_name, stage):
        version = self._latest_version(model_name)
        self.client.set_model_version_tag(
            name=model_name,
            version=version,
            key="app_stage",
            value=stage,
        )

    def _archive_models(self, tgt_model):
        for model, stage in self.list_models().items():
            if stage == "Production" and model != tgt_model:
                self.client.set_model_version_tag(
                    name=model,
                    version=self._latest_version(model),
                    key="app_stage",
                    value="Archived",
                )

    def list_models(self):
        models = {}
        for rm in self.client.search_registered_models():
            latest = self._latest_version(rm.name)
            mv = self.client.get_model_version(rm.name, latest)
            models[rm.name] = mv.tags.get("app_stage")
        return models

    def get_production_model(self):
        for name, stage in self.list_models().items():
            if stage == "Production":
                return name
        return None

    def set_model_stage(self, model_name, operation):
        if model_name not in self:
            return f"No action taken. `{model_name}` is not a valid model."

        tgt_stage = "Production" if operation == "elevate" else "Archived"
        current_stage = self._get_stage(model_name)

        if current_stage == tgt_stage:
            return f"No action taken. `{model_name}` already set to `{tgt_stage}`."

        self._set_stage(model_name, tgt_stage)

        if tgt_stage == "Production":
            self._archive_models(model_name)

        return f"`{model_name}` sucessfully set to `{tgt_stage}`."
