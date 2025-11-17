function SelectTool(user_message: string) -> ModelRegistryAPI | NonApprovedRequest | ModelStageAPI {
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

class NonApprovedRequest {
  intent "other" @description(#"
    Select this intent when none of the other options are appropriate.
  "#)
}

// TODO: add expected intents to tests...
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