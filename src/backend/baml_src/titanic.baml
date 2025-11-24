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
    try to reasonable guess what the values should be where possible.
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
     I want to test the model in production. I feel like I have to do a lot of chores around the house and everyone plays with my toys without me asking. ma and pa say that we have fancy tickets to this ship but they have all sorts of fancy stuff in our homes back in france where we live. Anyways, I hope to get that new set of GI joes for christmas this year.
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