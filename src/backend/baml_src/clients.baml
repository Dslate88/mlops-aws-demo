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

client<llm> DEFAULT {
  provider aws-bedrock
  options {
    model "anthropic.claude-3-5-sonnet-20240620-v1:0"
    region us-east-1
    inference_configuration {
      max_tokens 100
      temperature 0.0
    }
  }
}
