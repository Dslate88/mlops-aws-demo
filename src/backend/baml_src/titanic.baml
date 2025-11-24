class TitanicInput {
  @@description(#"
    These are fields required prior to submitting inference call to a model.
  "#)
  sex SexTypes?
  pclass ClassTypes?
  embarked EmbarkTypes?
  age_group AgeGroupTypes?
  missing_details string[]? @description(#"
    This lists which, if any, of the fields the user did not provide.
  "#)
  reasoning string @description(#"
    relevant information from the user message related to what the fields might be.
  "#)
}

function TitanicValidateInput(user_message: string) -> TitanicInput {
  client "DEFAULT"
  prompt #"
    Given user message extract the relevant fields.
    Users may not provide any relevant fields, if that is the case, be sure to return all the fields in the missing_fields list.

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
      Test the currently active model
    "#
  }
}

test InputComplete {
  functions [TitanicValidateInput]
  args {
    user_message #"
     I'm a male age 5 who had a 2nd class ticket and I departed out of england.
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

enum AgeGroupTypes {
    ADULT
    CHILD
}