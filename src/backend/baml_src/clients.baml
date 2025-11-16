client<llm> OPENAIGPT4o {
  provider openai
  options {
    model "gpt-4o"
    api_key env.OPENAI_API_KEY
  }
}

client<llm> OPENAIGPT5 {
  provider openai
  options {
    model "gpt-5"
    api_key env.OPENAI_API_KEY
    supports_streaming false
  }
}

client<llm> OPENAIGPT5_NANO {
  provider openai
  options {
    model "gpt-5-nano"
    api_key env.OPENAI_API_KEY
    supports_streaming false
  }
}
