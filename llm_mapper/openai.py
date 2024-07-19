import os
from openai import OpenAI
from .prompt_utils import PromptUtils

class OpenAi:
  def __init__(self):
    # Get the OpenAI API key from environment variables
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
      raise ValueError("OpenAI API key is not set. Please check your .env file.")
    
    client = OpenAI(
      # This is the default and can be omitted
      api_key=api_key,
    )
    self.client = client

  # This method returns the output of the LLM
  def get_response(self, prompt):
    response = self.client.chat.completions.create(
      messages=[
        {
          "role": "user",
          "content": prompt,
        }
      ],
      model="gpt-3.5-turbo",
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content