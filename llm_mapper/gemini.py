import google.generativeai as genai
import os
from .prompt_utils import PromptUtils

class Gemini(PromptUtils):
  def __init__(self):
    # Get the OpenAI API key from environment variables
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
      raise ValueError("Gemini API key is not set. Please check your .env file.")
    
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    self.model = genai.GenerativeModel('gemini-pro')

  def get_response(self, query):
    response = self.model.generate_content(query)
    print(response.text)
    return response.text



