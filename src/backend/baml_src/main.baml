function SelectTool(user_message: string) -> ModelRegistryAPI | NonApprovedRequest {
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

test GeneralChat {
  functions [SelectTool]
  args {
    user_message #"
      Hi

    "#
  }
}