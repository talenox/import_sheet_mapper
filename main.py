from openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd
import csv
from datetime import datetime
from llm_mapper.openai import OpenAiMapper
from file_processor.file_processor import *
from static_data_generator.tlx_column_header_mapper import *

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

### Temp methods since there's no UI at the moment ###
def display_menu():
  print("Select a country/region:")
  print("1. Singapore")
  print("2. Malaysia")
  print("3. Hong Kong")
  print("4. Global")
  print("5. Indonesia")

def get_user_choice():
  choice = input("Enter the number corresponding to your choice: ")
  if choice == '1':
    return "singapore"
  elif choice == '2':
    return "malaysia"
  elif choice == '3':
    return "hong kong"
  elif choice == '4':
    return "global"
  elif choice == '5':
    return "indonesia"
  else:
    print("Invalid choice. Please try again.")
    return get_user_choice()
    
# Example function call
if __name__ == "__main__":
  display_menu()
  user_choice = get_user_choice()
  print(latest_version_contents(country=user_choice))
  # prompt = "Summarize the following CSV headers: name, age, email."
  # summary = llm_model.get_response(prompt)
  # print(summary)
