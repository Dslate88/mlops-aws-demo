class RegisteredModel {
  name string
  creation_timestamp string
  useful_info string
}

// TODO: Improve this shell logic later...
function ExtractModelInfo(models_info: string) -> RegisteredModel {
  client "openai-responses/gpt-5-mini"
  prompt #"
    These are mlflow.entity.RegisteredModels. Extract useful information...
    {{ models_info }}

    {{ ctx.output_format }}
  "#
}

test TestName {
  functions [ExtractModelInfo]
  args {
    models_info [
     "{'name': 'iris_rf_classifier', 'creation_timestamp': '1763316385175', 'last_updated_timestamp': '1763316694149', 'latest_versions': [{'name': 'iris_rf_classifier', 'version': '1', 'creation_timestamp': '1763316385221', 'last_updated_timestamp': '1763316694149', 'user_id': '', 'current_stage': 'Production', 'description': '', 'source': 'models:/m-13e2544afdde467896b73f7ddd88e2bf', 'run_id': 'c5c22f660a164b14ba926f34c5f466b7', 'status': 'READY', 'run_link': ''}, {'name': 'iris_rf_classifier', 'version': '4', 'creation_timestamp': '1763316694121', 'last_updated_timestamp': '1763316694121', 'user_id': '', 'current_stage': 'None', 'description': '', 'source': 'models:/m-b117b50be3af4a88a1c4a02f69ee4c93', 'run_id': '2f92fb827f8b436686f2b22689b2a827', 'status': 'READY', 'run_link': ''}], 'deployment_job_state': 'DEPLOYMENT_JOB_CONNECTION_STATE_UNSPECIFIED'}"
    ]
  }
}