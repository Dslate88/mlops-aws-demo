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
  client "DEFAULT"
  prompt #"
    Given user message extract the relevant info.

    {{ ctx.output_format }}

    {{ _.role('user') }}
    {{ user_message }}
  "#
}

class TitanicTrain {
  @@description(#"
    These are user selected config for training a machine learning model.
  "#)
  test_size float?
}

function TitanicValidateTrain(user_message: string) -> TitanicTrain {
  client "DEFAULT"
  prompt #"
    Extract the values for the relevant fields from the users message.

    {{ ctx.output_format }}

    {{ _.role('user') }}
    {{ user_message }}
  "#
}

test TrainComplete {
  functions [TitanicValidateTrain]
  args {
    user_message #"
      train model titanic set test size to 5.2
    "#
  }
}

test TrainMissing {
  functions [TitanicValidateTrain]
  args {
    user_message #"
      train titanic model
    "#
  }
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
