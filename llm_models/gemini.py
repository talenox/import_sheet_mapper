import google.generativeai as genai
import os
from .prompt_utils import PromptUtils
import streamlit as st

class Gemini(PromptUtils):
  def __init__(self):
    # Get the OpenAI API key from environment variables
    api_key = st.secrets.gemini.gemini_api_key
    if not api_key:
      raise ValueError("Gemini API key is not set. Please check your .env file.")
    
    genai.configure(api_key=api_key)
    self.model = genai.GenerativeModel('gemini-pro')

  def get_response(self, query):
    response = self.model.generate_content(query)
    return response.text



