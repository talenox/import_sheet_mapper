from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import streamlit as st
from llm_mapper.openai import OpenAiMapper
from file_processor.file_processor import *
from static_data_generator.tlx_column_header_mapper import *

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
  raise ValueError("OpenAI API key is not set. Please check your .env file.")

def get_uploaded_file():
  uploaded_file = st.file_uploader("Choose a file", type=["xlsx", "xls", "csv"])
  return uploaded_file

def generate_mappings(raw_data_headers, country_specific_tlx_import_sheet_headers):
  # Initialize the OpenAI client
  client = OpenAI(
    # This is the default and can be omitted
    api_key=api_key,
  )
  llm_model = OpenAiMapper(client)
  prompt = llm_model.create_mapping_prompt(raw_data_headers, country_specific_tlx_import_sheet_headers)
  response = llm_model.get_response(prompt)
  return response

def app():
  st.title("Upload and Process Excel/CSV File")
  uploaded_file = get_uploaded_file()
  if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
      sampled_df = read_csv_and_sample(uploaded_file)
      raw_data_headers = extract_headers_from_csv(uploaded_file)
    else:
      sampled_df = read_excel_and_sample(uploaded_file)
      raw_data_headers = extract_headers_from_excel_file(uploaded_file)
    st.write("File Uploaded Successfully.")
    st.write(sampled_df)

    country = st.selectbox("Select Country:", options=['SINGAPORE', 'MALAYSIA', 'HONG KONG', 'INDONESIA', 'GLOBAL'])

    if country:
      country_specific_tlx_import_sheet_headers = get_column_headers(country.lower().replace(" ", "_"))
      initial_mappings = generate_mappings(raw_data_headers, country_specific_tlx_import_sheet_headers)
      # initial_mappings = '''
      #   {
      #     "Employee ID": "Employee ID*",
      #     "First Name": "First Name",
      #     "Last Name": "Last Name",
      #     "Nickname": "Nickname",
      #     "Chinese Name": "Chinese Name",
      #     "Email": "Email Address",
      #     "Invite User": "Invite User*",
      #     "User Email (if different from employee email)": "User Email (if different from employee email)",
      #     "Access Role": "Access Role",
      #     "My Profile Module": "My Profile Module",
      #     "Payslip Module": "Payslip Module",
      #     "Tax Module": "Tax Module",
      #     "Leave Module": "Leave Module",
      #     "Payroll Module": "Payroll Module",
      #     "Profile Module": "Profile Module",
      #     "Birth Date (DD/MM/YYYY)": "Birth Date (DD/MM/YYYY)",
      #     "Gender": "Gender",
      #     "Marital Status": "Marital Status",
      #     "Identification Number": "Identification Number*",
      #     "Immigration Status": "Immigration Status*",
      #     "Contact Number": "Contact Number",
      #     "Office Direct Inward Dialing (DID) Number": "Office Direct Inward Dialing (DID) Number",
      #     "Address Line 1": "Address Line 1",
      #     "Address Line 2": "Address Line 2",
      #     "Country": "Country",
      #     "Region": "Region",
      #     "Subregion": "Subregion",
      #     "Postal Code": "Postal Code"
      #   }
      # '''
      initial_mappings_cleaned = initial_mappings.replace('\n', '')
      initial_mappings_json = json.loads(initial_mappings_cleaned)

      st.write("Please review and correct the mappings:")

      corrected_mappings = {}
      key = 0
      country_specific_tlx_import_sheet_headers = [""] + country_specific_tlx_import_sheet_headers
      for user_header, initial_map in initial_mappings_json.items():
        # Set initial value to the index of initial_map if it exists, else default to 0
        initial_index = country_specific_tlx_import_sheet_headers.index(initial_map) if initial_map in country_specific_tlx_import_sheet_headers else 0
        # Create a column layout
        col1, col2 = st.columns([3, 3])
        # Add text box for user header in the first column
        with col1:
          user_header_input = st.text_input(f"User Header for '{user_header}':", user_header, disabled=True)
        # Add dropdown for predefined header in the second column
        with col2:
          corrected = st.selectbox(f"Predefined Header for '{user_header}':", country_specific_tlx_import_sheet_headers, index=initial_index,key=key)
          key += 1
        corrected_mappings[user_header_input] = corrected

      if st.button("Submit Mappings"):
        st.write("Final Corrected Mappings:", corrected_mappings)

# Example function call
if __name__ == "__main__":
  app()
  # display_menu()
  # user_choice = get_user_choice()
  # country_specific_tlx_import_sheet_headers = get_column_headers(country=user_choice)
  # raw_data_headers = "name, birthdate, address"
  # prompt = llm_model.create_mapping_prompt(raw_data_headers, country_specific_tlx_import_sheet_headers)
  # response = llm_model.get_response(prompt)
  # print(response)