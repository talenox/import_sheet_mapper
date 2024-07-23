from openai import OpenAI
from dotenv import load_dotenv
import re
import os
import json
import streamlit as st
import warnings
from llm_mapper.openai import OpenAi
from llm_mapper.gemini import Gemini
from file_processor.extractor import *
from static_data_generator.tlx_column_header_mapper import *

# Load environment variables from .env file
load_dotenv()
# Suppress openpyxl warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

####################################################
COUNTRY_OPTIONS = ['SINGAPORE', 'MALAYSIA', 'HONG KONG', 'INDONESIA', 'GLOBAL']

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
      user_header_input = st.text_input(f"User Header for '{header}':", header, disabled=True, key=f"user_defined_header_{key}")
    with col2:
      if highlight:   # For suggested mappings
        corrected = st.selectbox(f"Predefined Header for '{header}':", country_specific_tlx_import_sheet_headers, index=index, key=key, format_func=lambda x: f'🔴 {x}' if x == value['column'] else x)
        st.text(f"{value['explanation']}")
      else:
        corrected = st.selectbox(f"Predefined Header for '{header}':", country_specific_tlx_import_sheet_headers, index=index, key=key)
    return user_header_input, corrected

  key = 0
  for user_header, initial_map in initial_mappings_json.items():
    if user_header.lower() in ["suggestion", "suggestions"] and isinstance(initial_map, dict):
      for suggestion_header, suggestion_value in initial_map.items():
        index = country_specific_tlx_import_sheet_headers.index(suggestion_value['column']) if suggestion_value['column'] in country_specific_tlx_import_sheet_headers else 0
        user_header_input, corrected = create_input_and_selectbox(suggestion_header, suggestion_value, index, key, highlight=True)
        st.session_state.corrected_mappings[user_header_input] = corrected
        key += 1
    else:
      index = country_specific_tlx_import_sheet_headers.index(initial_map) if initial_map in country_specific_tlx_import_sheet_headers else 0
      user_header_input, corrected = create_input_and_selectbox(user_header, initial_map, index, key)
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
        output = generate_column_dropdown_value_mappings(llm_model, target_col.lower(), data[source_col].unique())
        data_mappings = sanitise_output(output)
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

def sanitise_output(output):
  # Regex pattern to match JSON object
  pattern = re.compile(r'({.*?})', re.DOTALL)
  match = pattern.search(output)
  
  if match:
    # Extract the JSON object string
    json_str = match.group(1)
    # Convert the JSON string to a Python dictionary
    try:
      json_obj = json.loads(json_str)
      return json_obj
    except json.JSONDecodeError as e:
      return None
  else:
    return None

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
        #   {
        #     "Employee ID": "Employee ID",
        #     "First Name*": "First Name",
        #     "Last Name*": "Last Name",
        #     "Nickname": "Nickname",
        #     "Chinese Name": "Chinese Name",
        #     "Email": "Email",
        #     "Invite User*": "Invite User",
        #     "User Email (if different from employee email)": "User Email (if different from employee email)",
        #     "Access Role": "Access Role",
        #     "My Profile Module": "My Profile Module",
        #     "Payslip Module": "Payslip Module",
        #     "Tax Module": "Tax Module",
        #     "Leave Module": "Leave Module",
        #     "Payroll Module": "Payroll Module",
        #     "Profile Module": "Profile Module",
        #     "Claims Module (User)": "Claims Module (User)",
        #     "Claims Module (Admin)": "Claims Module (Admin)",
        #     "Birth Date (DD/MM/YYYY)*": "Birth Date (DD/MM/YYYY)",
        #     "Gender": "Gender",
        #     "Marital Status": "Marital Status",
        #     "Identification No*": "Identification No",
        #     "Immigration Status*": "Immigration Status",
        #     "PR Status": "PR Status",
        #     "PR Effective Date (DD/MM/YYYY)": "PR Effective Date (DD/MM/YYYY)",
        #     "S Pass Issue Date (DD/MM/YYYY)": "S Pass Issue Date (DD/MM/YYYY)",
        #     "S Pass Expiry Date (DD/MM/YYYY)": "S Pass Expiry Date (DD/MM/YYYY)",
        #     "S Pass Dependency Ceiling": "S Pass Dependency Ceiling",
        #     "E Pass Issue Date (DD/MM/YYYY)": "E Pass Issue Date (DD/MM/YYYY)",
        #     "E Pass Expiry Date (DD/MM/YYYY)": "E Pass Expiry Date (DD/MM/YYYY)",
        #     "Letter of Consent Issue Date (DD/MM/YYYY)": "Letter of Consent Issue Date (DD/MM/YYYY)",
        #     "Letter of Consent Expiry Date (DD/MM/YYYY)": "Letter of Consent Expiry Date (DD/MM/YYYY)",
        #     "Personalised Employment Pass Issue Date (DD/MM/YYYY)": "Personalised Employment Pass Issue Date (DD/MM/YYYY)",
        #     "Personalised Employment Pass Expiry Date (DD/MM/YYYY)": "Personalised Employment Pass Expiry Date (DD/MM/YYYY)",
        #     "Work Pass Number": "Work Pass Number",
        #     "Work Pass Issue Date (DD/MM/YYYY)": "Work Pass Issue Date (DD/MM/YYYY)",
        #     "Work Pass Expiry Date (DD/MM/YYYY)": "Work Pass Expiry Date (DD/MM/YYYY)",
        #     "Work Pass Dependency Ceiling": "Work Pass Dependency Ceiling",
        #     "Work Pass Worker Category": "Work Pass Worker Category",
        #     "Tech Pass Issue Date (DD/MM/YYYY)": "Tech Pass Issue Date (DD/MM/YYYY)",
        #     "Tech Pass Expiry Date (DD/MM/YYYY)": "Tech Pass Expiry Date (DD/MM/YYYY)",
        #     "ONE Pass Issue Date (DD/MM/YYYY)": "ONE Pass Issue Date (DD/MM/YYYY)",
        #     "ONE Pass Expiry Date (DD/MM/YYYY)": "ONE Pass Expiry Date (DD/MM/YYYY)",
        #     "Training Employment Pass Issue Date (DD/MM/YYYY)": "Training Employment Pass Issue Date (DD/MM/YYYY)",
        #     "Training Employment Pass Expiry Date (DD/MM/YYYY)": "Training Employment Pass Expiry Date (DD/MM/YYYY)",
        #     "Training Work Permit Issue Date (DD/MM/YYYY)": "Training Work Permit Issue Date (DD/MM/YYYY)",
        #     "Training Work Permit Expiry Date (DD/MM/YYYY)": "Training Work Permit Expiry Date (DD/MM/YYYY)",
        #     "Identification Issue Date (DD/MM/YYYY)": "Identification Issue Date (DD/MM/YYYY)",
        #     "Identification Expiry Date (DD/MM/YYYY)": "Identification Expiry Date (DD/MM/YYYY)",
        #     "Passport No": "Passport No.",
        #     "Passport Date of Issue (DD/MM/YYYY)": "Passport Date of Issue (DD/MM/YYYY)",
        #     "Passport Date of Expiry (DD/MM/YYYY)": "Passport Date of Expiry (DD/MM/YYYY)",
        #     "Passport Place of Issue": "Passport Place of Issue",
        #     "Nationality": "Nationality",
        #     "Race": "Race",
        #     "Religion": "Religion",
        #     "Job Title": "Job Title",
        #     "Hired Date (DD/MM/YYYY)*": "Hired Date (DD/MM/YYYY)",
        #     "Job Start Date (DD/MM/YYYY)": "Job Start Date (DD/MM/YYYY)",
        #     "Department": "Department",
        #     "Location/Branch": "Location/Branch",
        #     "Default Cost Centre": "Default Cost Centre",
        #     "Role": "Role",
        #     "Confirmation Date (DD/MM/YYYY)": "Confirmation Date (DD/MM/YYYY)",
        #     "Working Day*": "Working Day",
        #     "Working Hour*": "Working Hour",
        #     "Rate of Pay*": "Rate of Pay",
        #     "Currency of Salary*": "Currency of Salary",
        #     "Basic Salary*": "Basic Salary",
        #     "Designation in Accounting Software": "Designation in Accounting Software",
        #     "Job Remarks": "Job Remarks",
        #     "Resign Date (DD/MM/YYYY)": "Resign Date (DD/MM/YYYY)",
        #     "Payment Method*": "Payment Method",
        #     "Bank Type": "Bank Type",
        #     "Bank Account Holders Name": "Bank Account Holder's Name",
        #     "Bank Account No.": "Bank Account No.",
        #     "Bank Branch No.": "Bank Branch No.",
        #     "SHG Automation*": "Automatically calculate SHG",
        #     "SHG Contribution*": "SHG Contribution",
        #     "Additional SHG Contribution*": "Additional SHG Contribution",
        #     "Contact Number": "Contact Number",
        #     "Office Direct Inward Dialing (DID) Number": "Office Direct Inward Dialing (DID) Number",
        #     "Address Line 1": "Address Line 1",
        #     "Country": "Country",
        #     "Region": "Region",
        #     "Subregion": "Subregion",
        #     "Postal Code": "Postal Code",
        #     "Next of Kins Name": "Next of Kin's Name",
        #     "Next of Kins Nationality": "Next of Kin's Nationality",
        #     "Next of Kins Gender": "Next of Kin's Gender",
        #     "Next of Kins Birth Date (DD/MM/YYYY)": "Next of Kin's Birth Date (DD/MM/YYYY)",
        #     "Next of Kins Identification No": "Next of Kin's Identification No.",
        #     "Next of Kins Passport No": "Next of Kin's Passport No.",
        #     "Next of Kins Relationship": "Next of Kin's Relationship",
        #     "Next of Kins Marriage Date (Spouse) (DD/MM/YYYY)": "Next of Kin's Marriage Date (Spouse) (DD/MM/YYYY)",
        #     "Next of Kins Contact No": "Next of Kin's Contact No.",
        #     "Covid-19 Vaccination Status": "Covid-19 Vaccination Status",
        #     "Covid-19 Vaccine Brand": "Covid-19 Vaccine Brand",
        #     "Date of 1st Dose (DD/MM/YYYY)": "Date of 1st Dose (DD/MM/YYYY)",
        #     "Date of 2nd Dose (DD/MM/YYYY)": "Date of 2nd Dose (DD/MM/YYYY)",
        #     "Covid-19 Vaccine Booster Brand": "Covid-19 Vaccine Booster Brand",
        #     "Date of Booster Dose (DD/MM/YYYY)": "Date of Booster Dose (DD/MM/YYYY)",
        #     "Vaccination Remarks": "Vaccination Remarks",
        #     "Halal Certification Issue Date (DD/MM/YYYY)": "Halal Certification Issue Date (DD/MM/YYYY)",
        #     "Halal Certification Expiry Date (DD/MM/YYYY)": "Halal Certification Expiry Date (DD/MM/YYYY)",
        #     "Hygiene Certification Issue Date (DD/MM/YYYY)": "Hygiene Certification Issue Date (DD/MM/YYYY)",
        #     "Hygiene Certification Expiry Date (DD/MM/YYYY)": "Hygiene Certification Expiry Date (DD/MM/YYYY)",
        #     "Workday Import Fields": "Custom Fields Hash",
        #     "asd": "Overwrite Jobs Array (Ignore current jobs columns)",
        #     "Suggestion": {
        #       "Position": {
        #         "column": "Job Title",
        #         "explanation": "based on the sample values and contextual meaning"
        #       }
        #     }
        #   }
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
  
  # Initialize the Gemini client
  llm_model = Gemini()
  app(llm_model)