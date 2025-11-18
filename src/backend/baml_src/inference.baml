class ModelInput {
  @@description(#"
    These are fields required prior to submitting inference call to a model.
  "#)
  sex SexTypes?
//   pclass "First"? | "Second"? | "Third"?
  pclass ClassTypes?
  embarked EmbarkTypes?
  alone AloneTypes?
  missing_details string[]? @description(#"
    This lists which, if any, of the fields the user did not provide.
  "#)
}

function ValidateInput(user_message: string) -> ModelInput {
  client "openai/gpt-5-mini"
  prompt #"
    Given user message extract the relevant info.

    {{ ctx.output_format }}

    {{ _.role('user') }}
    {{ user_message }}
  "#
}

test InputMissing {
  functions [ValidateInput]
  args {
    user_message #"
        I'm a male in second class and i embarked out of canada
    "#
  }
}

test InputComplete {
  functions [ValidateInput]
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



// feed = {
//     "sex":      np.array([[sex]], dtype=object),
//     "pclass":   np.array([[pclass]], dtype=np.int64),
//     "embarked": np.array([[embarked]], dtype=object),
//     "alone":    np.array([[alone]], dtype=np.int64),
// }

// {
//   "pclass": {
//     "1": "First Class",
//     "2": "Second Class",
//     "3": "Third Class"
//   },
//   "embarked": {
//     "S": "Southampton (England)",
//     "C": "Cherbourg (France)",
//     "Q": "Queenstown (Ireland)"
//   },
//   "alone": {
//     "0": "Not Alone (with family)",
//     "1": "Alone (no family aboard)"
//   }
// }
