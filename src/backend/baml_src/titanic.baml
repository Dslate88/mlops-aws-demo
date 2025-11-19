class TitanicInput {
  @@description(#"
    These are fields required prior to submitting inference call to a model.
  "#)
  sex SexTypes?
  pclass ClassTypes?
  embarked EmbarkTypes?
  alone AloneTypes?
  missing_details string[]? @description(#"
    This lists which, if any, of the fields the user did not provide.
  "#)
}

function TitanicValidateInput(user_message: string) -> TitanicInput {
  client "openai/gpt-5-mini"
  prompt #"
    Given user message extract the relevant info.

    {{ ctx.output_format }}

    {{ _.role('user') }}
    {{ user_message }}
  "#
}

test InputMissing {
  functions [TitanicValidateInput]
  args {
    user_message #"
        I'm a male in second class and i embarked out of canada
    "#
  }
}

test InputComplete {
  functions [TitanicValidateInput]
  args {
    user_message #"
        I'm a male in second class and i embarked out of england alone
    "#
  }
}

enum SexTypes {
    MALE
    FEMALE
}

enum ClassTypes {
    FIRST
    SECOND
    THIRD
}

enum EmbarkTypes {
    ENGLAND
    FRANCE
    IRELAND
}

enum AloneTypes {
    TRUE
    FALSE
}