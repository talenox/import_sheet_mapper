from openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd
import csv
from llm_mapper.openai import OpenAiMapper
from file_processor.file_processor import *

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
  raise ValueError("OpenAI API key is not set. Please check your .env file.")

# Initialize the OpenAI client
client = OpenAI(
  # This is the default and can be omitted
  api_key=api_key,
)

llm_model = OpenAiMapper(client)

# Example function call
if __name__ == "__main__":
  prompt = "Summarize the following CSV headers: name, age, email."
  summary = llm_model.get_response(prompt)
  print(summary)
