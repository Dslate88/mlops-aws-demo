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
  intent "list_registered_models"
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