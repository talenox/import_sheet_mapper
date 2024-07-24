from openai import OpenAI
from dotenv import load_dotenv
import json
import streamlit as st
import warnings
from llm_models.openai import OpenAi
from llm_models.gemini import Gemini
from data_processor.extractor import *
from data_generator.tlx_column_header_mapper import *
from helper_methods.mapper import *
from helper_methods.display import *

# Load environment variables from .env file
load_dotenv()
# Suppress openpyxl warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

####################################################
COUNTRY_OPTIONS = ['SINGAPORE', 'MALAYSIA', 'HONG KONG', 'INDONESIA', 'GLOBAL']

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
        # initial_mappings = generate_column_header_mappings(llm_model, raw_data_headers, user_sample_values, country_specific_tlx_import_sheet_headers, country_specific_sample_values)
        initial_mappings = '''{
          "EmployeeCode": "Employee ID",
          "LastName": "Last Name",
          "FirstName": "First Name",
          "MiddleName": null,
          "EmployeeName": null,
          "AliasName": "Nickname",
          "Gender": "Gender",
          "Title": null,
          "NationalityCode": "Nationality",
          "BirthDate": "Birth Date (DD/MM/YYYY)",
          "BirthPlace": null,
          "RaceCode": "Race",
          "ReligionCode": "Religion",
          "MaritalStatus": "Marital Status",
          "MarriageDate": null,
          "Email": "Email",
          "Funds": null,
          "MOMOccupationCode": null,
          "MOMEmployeeType": null,
          "MOMOccupationGroup": null,
          "MOMCategory": null,
          "WorkDaysPerWeek": "Working Day",
          "WorkHoursPerDay": "Working Hour",
          "WorkHoursPerYear": null,
          "BankAccountNo": "Bank Account No.",
          "BankBranch": "Bank Branch No.",
          "BankCode": null,
          "BankCurrencyCode": null,
          "CPFMethodCode": null,
          "CPFEmployeeType": null,
          "FWLCode": null,
          "Suggestion": {
            "SCF01": {
              "column": "Mailing Address",
              "explanation": "based on the context of providing an address"
            }
          }
        }
        '''
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
        display_mapped_data(llm_model, data, st.session_state.corrected_mappings, country_specific_tlx_import_sheet_headers[1:])

        # Write to the preformatted file
        # write_to_preformatted_excel(data, corrected_mappings, country_specific_tlx_import_sheet_headers[1:], st.session_state.confirmed_country)

if __name__ == "__main__":
  # st.session_state.clear()
  # Initialize the OpenAI client
  # llm_model = OpenAi()
  
  # Initialize the Gemini client
  llm_model = Gemini()
  app(llm_model)