function SelectTool(user_message: string) -> ModelRegistryAPI | NonApprovedRequest | ModelStageAPI | ModelInferenceAPI {
  client "openai/gpt-5-mini"
  prompt #"
    You are a router. Decide which intent fits best and populate the fields.

    Examples:
    - Use ModelRegistryAPI for questions like:
      - "What models are available?"
      - "Which models do I have?"
    - Use ModelStageAPI for model elevation/archival like:
      - "Elevate titanic to production"
      - "Take titanic off production"
      - "Archive titanic"
    - Use ModelInferenceAPI when the user wants to test/run/predict with the model:
      - "I want to test the model in production"
      - "Run a prediction with the production model"
    - Use NonApprovedRequest for anything else.

    {{ ctx.output_format }}

    {{ _.role('user') }}
    {{ user_message }}
  "#
}

// TODO: implement action list later...
class ModelRegistryAPI {
  intent "model_registry" @description(#"
    User is asking questions related to machine learning models in the registry.
  "#)
}

class ModelStageAPI {
  intent "model_stage_changes" @description(#"
    User either wants to elevate or archive a machine learning model.
  "#)
  operation "elevate" | "archive"
  model_name string
}

class ModelInferenceAPI {
  intent "model_inference" @description(#"
    User wants to test/predict/score a model to see its result.
  "#)
}

class NonApprovedRequest {
  intent "other" @description(#"
    Select this intent when none of the other options are appropriate.
  "#)
}

// TODO: add expected intents to tests...
test ModelInference {
  functions [SelectTool]
  args {
    user_message #"
      I want to test a model
    "#
  }
}

test ModelList {
  functions [SelectTool]
  args {
    user_message #"
      What models are available?
    "#
  }
}

test ModelStage {
  functions [SelectTool]
  args {
    user_message #"
      take model_a off production
    "#
  }
}

test GeneralChat {
  functions [SelectTool]
  args {
    user_message #"
      Hi
    "#
  }
}