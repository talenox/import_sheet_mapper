from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import streamlit as st
import warnings
from llm_mapper.openai import OpenAi
from llm_mapper.gemini import Gemini
from file_processor.file_processor import *
from static_data_generator.tlx_column_header_mapper import *

# Load environment variables from .env file
load_dotenv()

# Suppress openpyxl warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

####################################################
COUNTRY_OPTIONS = ['SINGAPORE', 'MALAYSIA', 'HONG KONG', 'INDONESIA', 'GLOBAL']

# This method extracts a list of header column names and some sample data for display purposes
def extract_header_and_sample_data(uploaded_file, rows_to_skip):
  if uploaded_file.name.endswith('.csv'):
      sampled_df = read_csv_and_sample(uploaded_file)
      raw_data_headers = extract_headers_from_csv(uploaded_file)
  else:
    sampled_df = read_excel_and_sample(uploaded_file, rows_to_skip)
    raw_data_headers = extract_headers_from_excel_file(uploaded_file, rows_to_skip)
  
  return sampled_df, raw_data_headers

# This method extracts unique values for each column in the sheet and packs it up into a json to feed into the LLM prompt
def extract_unique_sample_values(uploaded_file, rows_to_skip, sheet_name=0):
  df = pd.read_excel(uploaded_file, sheet_name=sheet_name, skiprows=rows_to_skip)
  # Initialize dictionary to store sampled data lists
  sampled_data = {}

  # Iterate over columns in the DataFrame
  for col in df.columns:
    # Get unique non-NaN values from the column
    unique_values = df[col].dropna().unique()[:2].tolist()
    # Add to sampled_data if there are unique values
    if unique_values:
      sampled_data[col] = unique_values

  # Convert dictionary to JSON string with 2-space indentation
  sample_data = json.dumps(sampled_data, ensure_ascii=False, indent=2)
  
  return sample_data

# This method calls the LLM to create mappings based on the given column names and their data
def generate_column_header_mappings(llm_model, raw_data_headers, raw_sample_values, country_specific_tlx_import_sheet_headers, country_specific_sample_values):
  prompt = llm_model.create_column_header_mapping_prompt(raw_data_headers, raw_sample_values, country_specific_tlx_import_sheet_headers, country_specific_sample_values)
  response = llm_model.get_response(prompt)
  return response

# This method displays the initial mappings done by the LLM on the UI
def display_initial_mappings(initial_mappings_json, country_specific_tlx_import_sheet_headers):
    if 'corrected_mappings' not in st.session_state:
      st.session_state.corrected_mappings = {}

  country_specific_tlx_import_sheet_headers = [""] + country_specific_tlx_import_sheet_headers

  def create_input_and_selectbox(header, value, index, key, highlight=False):
    col1, col2 = st.columns([3, 3])
    with col1:
      user_header_input = st.text_input(f"User Header for '{header}':", header, disabled=True, key=header)
    with col2:
      if highlight:
        corrected = st.selectbox(f"Predefined Header for '{header}':", country_specific_tlx_import_sheet_headers, index=index, key=key, format_func=lambda x: f'🔴 {x}' if x == value else x)
      else:
        corrected = st.selectbox(f"Predefined Header for '{header}':", country_specific_tlx_import_sheet_headers, index=index, key=key)
    return user_header_input, corrected

  key = 0
  for user_header, initial_map in initial_mappings_json.items():
    if user_header == "Suggestion" and isinstance(initial_map, dict):
      for suggestion_header, suggestion_value in initial_map.items():
        initial_index = country_specific_tlx_import_sheet_headers.index(suggestion_value) if suggestion_value in country_specific_tlx_import_sheet_headers else 0
        user_header_input, corrected = create_input_and_selectbox(suggestion_header, suggestion_value, initial_index, key, highlight=True)
        st.session_state.corrected_mappings[user_header_input] = corrected
        key += 1
    else:
      initial_index = country_specific_tlx_import_sheet_headers.index(initial_map) if initial_map in country_specific_tlx_import_sheet_headers else 0
      user_header_input, corrected = create_input_and_selectbox(user_header, initial_map, initial_index, key)
      st.session_state.corrected_mappings[user_header_input] = corrected
      key += 1

  return st.session_state.corrected_mappings

# This method displays the final mappings done by the LLM and corrected by the user on the UI
def display_mapped_data(data, corrected_mappings, headers):
  fixed_value_columns = get_column_dropdown_values().keys()
  # Initialize an empty DataFrame with the specified headers
  mapped_data = pd.DataFrame(columns=headers)

  # Loop through mappings and populate the mapped_data DataFrame
  for source_col, target_col in corrected_mappings.items():
    # Only map if the source column exists in data and target column is in headers
    if source_col in data.columns and target_col in headers:
      if target_col.lower() in fixed_value_columns:
        data_mappings = json.loads(generate_column_dropdown_value_mappings(llm_model, target_col.lower(), data[source_col].unique()))
        # Replace the values in the user's sheet with what it was mapped to
        mapped_data[target_col] = data[source_col].apply(lambda x: data_mappings.get(x, x) if data_mappings.get(x, x) else x)
      else:
        mapped_data[target_col] = data[source_col]
  # Ensure all required headers are present, fill missing with empty strings
  for header in headers:
    if header not in mapped_data.columns:
      mapped_data[header] = ''
  
  # Display the mapped data in a DataFrame
  st.write("Mapped Data:")
  st.dataframe(mapped_data)

# This method generates the mappings for the column data
def generate_column_dropdown_value_mappings(llm_model, column_name, user_column_values):
  fixed_column_dropdown_values_json = get_column_dropdown_values()
  accepted_column_values = fixed_column_dropdown_values_json[column_name]
  prompt = llm_model.create_column_value_mapping_prompt(user_column_values, accepted_column_values)
  response = llm_model.get_response(prompt)
  return response

def app(llm_model):
  st.title("Talenox's import sheet mapper")
  uploaded_file = get_uploaded_file()
  # Input field for starting row number
  rows_to_skip = st.number_input("Enter the number of rows to skip. For example, if your data starts on the 3rd row, then input 2.", min_value=1, value=1)
  if uploaded_file is not None:
    sampled_df, raw_data_headers = extract_header_and_sample_data(uploaded_file, rows_to_skip)
    user_sample_values = extract_unique_sample_values(uploaded_file, rows_to_skip, sheet_name=0)
    
    st.write("File Uploaded Successfully.")
    st.write(sampled_df)

    if 'confirmed_country' not in st.session_state:
      st.session_state.confirmed_country = None
    country = st.selectbox("Select Country:", options=COUNTRY_OPTIONS)
    # Add a submit button to confirm the country selection
    if st.button("Confirm Country"):
      st.session_state.confirmed_country = country

    if st.session_state.confirmed_country:
      country_specific_tlx_import_sheet_headers = get_column_headers(st.session_state.confirmed_country.lower().replace(" ", "_"))
      country_specific_sample_values = get_sample_values(st.session_state.confirmed_country.lower().replace(" ", "_"))
      if 'initial_mappings' not in st.session_state:
        initial_mappings = generate_column_header_mappings(llm_model, raw_data_headers, user_sample_values, country_specific_tlx_import_sheet_headers, country_specific_sample_values)
        # initial_mappings = '''
        #   {  "EmployeeCode": "Employee ID",  "LastName": "Last Name",  "FirstName": "First Name",  "MiddleName": "Nickname (if different from employee first name)",  "AliasName": "Chinese Name",  "Gender": "Gender",  "Title": "Job Title",  "NationalityCode": "Nationality",  "BirthDate": "Birth Date (DD/MM/YYYY)",  "BirthPlace": "Passport Place of Issue",  "RaceCode": "Race",  "ReligionCode": "Religion",  "MaritalStatus": "Marital Status",  "MarriageDate": "Marriage Date (Spouse) (DD/MM/YYYY)",  "Email": "Email",  "Funds": "Payment Method",  "MOMOccupationCode": "Role",  "MOMEmployeeType": "Working Day",  "MOMOccupationGroup": "Department",  "MOMCategory": "Location/Branch",  "WorkDaysPerWeek": "Working Day",  "WorkHoursPerDay": "Working Hour",  "WorkHoursPerYear": "Rate of Pay",  "BankAccountNo": "Bank Account No.",  "BankBranch": "Bank Branch No.",  "BankCode": "Bank Type",  "BankCurrencyCode": "Currency of Salary",  "CPFMethodCode": "CPF in lieu",  "CPFEmployeeType": "Rate of Pay",  "FWLCode": "Confirmation Date (DD/MM/YYYY)",  "SFC01": "Overwrite Jobs Array (Ignore current jobs columns)"}
        # '''
        initial_mappings_cleaned = initial_mappings.replace('\n', '')
        initial_mappings_json = json.loads(initial_mappings_cleaned)
        st.session_state['initial_mappings'] = initial_mappings_json
      else:
        initial_mappings_json = st.session_state['initial_mappings']

      st.write("Please review and correct the mappings:")
      corrected_mappings = display_initial_mappings(initial_mappings_json, country_specific_tlx_import_sheet_headers)

      if st.button("Submit Mappings"):
        st.write("Final Corrected Mappings:", corrected_mappings)
        # Read the uploaded file again to get the full data
        data = pd.read_excel(uploaded_file, skiprows=rows_to_skip)
        display_mapped_data(data, st.session_state.corrected_mappings, country_specific_tlx_import_sheet_headers[1:])

        # Write to the preformatted file
        # write_to_preformatted_excel(data, corrected_mappings, country_specific_tlx_import_sheet_headers[1:], st.session_state.confirmed_country)

if __name__ == "__main__":
  # st.session_state.clear()
  # Initialize the OpenAI client
  # llm_model = OpenAi()
  # print(llm_model.get_response("What is the capital of Australia?"))
  
  # Initialize the Gemini client
  llm_model = Gemini()
  # print(llm_model.get_response("What is the capital of Australia?"))
  app(llm_model)