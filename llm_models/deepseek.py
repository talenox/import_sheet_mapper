import os

from openai import OpenAI

from .prompt_utils import PromptUtils


class DeepSeek(PromptUtils):
  def __init__(self):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
      raise ValueError(
        "DeepSeek API key is not set. Add DEEPSEEK_API_KEY to your "
        "Streamlit secrets or .env file."
      )

    self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-flash")
    self.client = OpenAI(
      api_key=api_key,
      base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    )

  def get_response(self, prompt):
    response = self.client.chat.completions.create(
      messages=[
        {
          "role": "user",
          "content": prompt,
        }
      ],
      model=self.model,
    )
    return response.choices[0].message.content
