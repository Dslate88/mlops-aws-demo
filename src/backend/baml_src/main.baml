function SelectTool(user_message: string) -> ModelRegistryAPI | NonApprovedRequest | ModelStageAPI | ModelInferenceAPI {
  client "openai/gpt-5-mini"
  prompt #"
    Given a message, extract info.
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
  model_name string?
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