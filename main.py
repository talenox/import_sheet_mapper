from openai import OpenAI
from dotenv import load_dotenv
import json
import streamlit as st
import warnings
from collections import Counter
from llm_models.openai import OpenAi
from llm_models.gemini import Gemini
from data_processor.extractor import *
from data_generator.tlx_column_header_mapper import *
from helper_methods.mapper import *
from helper_methods.display_mappings import *
from helper_methods.normalise_string import *
from app_state import AppState

# Load environment variables from .env file
load_dotenv()
# Suppress openpyxl warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

####################################################
COUNTRY_OPTIONS = ['SINGAPORE', 'MALAYSIA', 'HONG KONG', 'INDONESIA', 'GLOBAL']

# This method initialises all the necessary variables at the start of the program
def initialise_session_state_variables():
  if 'app_state' not in st.session_state:
    st.session_state.app_state = AppState.display_file_uploader
  if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
  if 'confirmed_country' not in st.session_state:
    st.session_state.confirmed_country = None
  if 'corrected_column_mappings' not in st.session_state:
    st.session_state.corrected_column_mappings = {}
  if 'previous_confirmed_country' not in st.session_state:
    st.session_state.previous_confirmed_country = None
  if 'column_header_name_normalised_mapping' not in st.session_state:
    st.session_state['column_header_name_normalised_mapping'] = {}
  if 'consolidated_corrected_value_mappings' not in st.session_state:
    st.session_state['consolidated_corrected_value_mappings'] = {}
  if 'mapped_data' not in st.session_state:
    st.session_state['mapped_data'] = pd.DataFrame()
  if 'column_header_name_normalised_mapping' not in st.session_state:
    st.session_state['column_header_name_normalised_mapping'] = {}

# This method renders the Upload File section. Only excel sheets are supported at the moment
def render_upload_file_widget():
  st.subheader("Choose a file")
  uploaded_file = st.file_uploader("Upload the file containing your data.", type=["xlsx", "xls"])
  if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file
    st.session_state.app_state = AppState.display_country_selector

# This method renders the section to allow users to set the header row of the sheet uploaded
def render_sheet_skiprow_widget():
    rows_to_skip = st.number_input("Enter the number of rows to skip. For example, if your data starts on the 3rd row, then input 2.", min_value=1, value=1)
    return rows_to_skip

# This method displays the first 5 rows of the uploaded sheet
def render_uploaded_file_head_widget(sampled_df):
  st.write("File Uploaded Successfully.")
  st.write(sampled_df)

# This method renders the dropdown for users to choose the country import sheet to map to
def render_select_country_widget():
  st.subheader("Select Country")
  country = st.selectbox("Talenox has a differently formatted import sheet for each country.", options=COUNTRY_OPTIONS)
  return normalise_column_name(country)

def render_confirm_country_button(country):
  if st.button("Confirm Country"):
    st.session_state.confirmed_country = country
    st.session_state.corrected_column_mappings = {}
    st.session_state['consolidated_intial_value_mappings'] = {}
    st.session_state['consolidated_corrected_value_mappings'] = {}
    st.session_state['mapped_data'] = pd.DataFrame()
    st.session_state['initial_mappings'] = None
    st.session_state['column_header_name_normalised_mapping'] = load_column_header_name_normalised_mapping()
    st.session_state.app_state = AppState.display_column_header_mapping

# This method hits the LLM to generate the column header mappings
def get_column_header_mappings(llm_model, raw_data_headers, user_sample_values, country_specific_tlx_import_sheet_headers):
  country_specific_sample_values = get_sample_values(st.session_state.confirmed_country.lower().replace(" ", "_"))
  # Only hit the LLM if the session state does not already contain the mappings. When user changes country, initial_mappings will be reset, triggering the if block below
  if st.session_state.initial_mappings is None:
    # initial_mappings = generate_column_header_mappings(llm_model, raw_data_headers, user_sample_values, st.session_state['column_header_name_normalised_mapping'].values(), country_specific_sample_values)
    initial_mappings = '''{
      "EmployeeCode": "Employee ID",
      "LastName": "Last Name*",
      "FirstName": "First Name*",
      "Gender": "Gender",
      "Title": "Job Title",
      "NationalityCode": "Nationality",
      "BirthDate": "Hired Date (DD/MM/YYYY)*",
      "RaceCode": "Race",
      "ReligionCode": "Religion",
      "MaritalStatus": "Marital Status",
      "Email": "Email",
      "BankAccountNo": "Bank Account No.",
      "BankBranch": "Bank Code",
      "BankCurrencyCode": {
        "column": "Currency of Salary",
        "explanation": "Based on the context of mapping currency"
      },
      "SFC01": "Nickname"
    }
    '''
    initial_mappings_cleaned = initial_mappings.replace('\n', '')
    initial_mappings_json = json.loads(initial_mappings_cleaned)
    st.session_state['initial_mappings'] = initial_mappings_json
  else:
    initial_mappings_json = st.session_state['initial_mappings']
  return initial_mappings_json

# This method renders the component to allow users to correct the initial mappings made by the LLM
def render_review_column_header_mapping_widget(initial_mappings, country_specific_tlx_import_sheet_headers):
  st.header("Column Header Mappings")
  st.write("Please review and modify (if necessary) the proposed mappings:")
  corrected_column_mappings = display_initial_column_mappings(initial_mappings, "corrected_column_mappings")
  return corrected_column_mappings

def render_submit_column_header_mapping_button(corrected_column_mappings):
  if st.button("Submit Column Mappings"):
    # here we should check if there are two user columns mapped to the same column header. if there are, we raise an error. otherwise, we continue as normal
    mapping_duplicates = get_column_mapping_duplicates()
    if len(mapping_duplicates) > 0:
      error_message = "Duplicate values found in the column mappings:\n"
      for value, count in mapping_duplicates.items():
        error_message += f"- Value '{value}' is mapped to {count} different keys.\n"
      st.error(error_message)
    else:
      st.write("Here are the confirmed column mappings.")
      with st.expander("Corrected Column Mappings:", expanded=False):
        st.write("", st.session_state.corrected_column_mappings)
      st.session_state.app_state = AppState.display_column_value_mapping

# This method checks and returns any duplicates found in the column header mappings submitted by user
def get_column_mapping_duplicates():
  # Step 1: Count the occurrences of each value in the dictionary
  value_counts = Counter(st.session_state.corrected_column_mappings.values())
  # Step 2: Find the duplicate values (those with more than one occurrence)
  duplicates = {value: count for value, count in value_counts.items() if count > 1 and value != ''}
  return duplicates

# This method hits the LLM to map values in fixed-value columns that have been mapped by the user
def generate_initial_fixed_column_value_mapping_widget(llm_model, consolidated_accepted_column_values, data):
  for user_column, tlx_column in st.session_state.corrected_column_mappings.items():
    normalised_column_name = normalise_column_name(tlx_column)
    if normalised_column_name in consolidated_accepted_column_values:
      accepted_column_values = consolidated_accepted_column_values[normalised_column_name]
      initial_value_mappings = generate_fixed_value_column_mappings(
        llm_model,
        data[user_column].unique().tolist(),
        accepted_column_values
      )
      st.session_state['consolidated_corrected_value_mappings'][normalised_column_name] = initial_value_mappings
  return None

# This method renders the component to allow users to correct the value mappings made by the LLM
def render_review_fixed_column_value_mapping_widget(corrected_column_mappings, consolidated_accepted_column_values, data):
  st.header("Column Value Mappings")
  st.write("Please review and modify (if necessary) the proposed mappings:")
  for _, tlx_column in corrected_column_mappings.items():
    normalised_column_name = normalise_column_name(tlx_column)
    if normalised_column_name in consolidated_accepted_column_values:
      accepted_column_values = consolidated_accepted_column_values[normalised_column_name]
      initial_value_mappings = st.session_state['consolidated_corrected_value_mappings'][normalised_column_name]
      
      st.subheader(f"{tlx_column}")
      corrected_value_mappings = display_initial_value_mappings(
        initial_value_mappings,
        accepted_column_values,
        f"{tlx_column}_corrected_value_mappings"
      )
      # Update the session state with the corrected mappings
      st.session_state['consolidated_corrected_value_mappings'][tlx_column] = corrected_value_mappings

def render_submit_fixed_column_value_mapping_button():
  if st.button("Submit Column Value Mappings"):
    st.session_state.app_state = AppState.display_column_default_value_selector

# This method renders the component to allow users to choose the default value for mandatory columns that have not been mapped
def render_choose_default_value_for_required_columns_widget():
  st.header("Default Column Values")
  # list all the unmapped values that are in mandatory_fixed_value_columns.txt
  mandatory_columns_normalized = [normalise_column_name(col) for col in get_mandatory_columns(st.session_state.confirmed_country)]
  mapped_columns_normalized = [normalise_column_name(col) for col in list(st.session_state.corrected_column_mappings.values())]
  unmapped_mandatory_columns = [normalise_column_name(column) for column in mandatory_columns_normalized if column not in mapped_columns_normalized]
  # pull the column dropdown values that are available
  column_dropdown_values = get_tlx_column_dropdown_values(st.session_state.confirmed_country)
  filtered_json = { key: column_dropdown_values[key] for key in unmapped_mandatory_columns if key in column_dropdown_values.keys() }
  # for each of them, choose a default value from column_dropdown_values.json or shared_columndropdown_values.json 
  display_default_value_mappings(filtered_json, "unmapped_columns_default_value")

def render_confirm_unmapped_column_default_values_button():
  if st.button("Confirm Default Values"):
    st.session_state.app_state = AppState.display_download_import_sheet_button

# This method renders the first few rows of the final import sheet after the data has been ported over
def render_final_import_sheet(uploaded_file, rows_to_skip, country_specific_tlx_import_sheet_headers):
  # Read the uploaded file again to get the full data
  data = pd.read_excel(uploaded_file, skiprows=rows_to_skip, dtype="str")
  st.session_state.mapped_data = display_final_mapped_data(data, st.session_state.corrected_column_mappings, country_specific_tlx_import_sheet_headers[1:], st.session_state['consolidated_corrected_value_mappings'], st.session_state.confirmed_country)

# This method prepares the final excel sheet to be downloaded by user
def render_download_import_sheet_button():
  write_to_preformatted_excel(st.session_state.mapped_data, st.session_state.confirmed_country)

# This method renders a back button for users to go back to the previous step
def render_back_button():
  if st.session_state.app_state == AppState.display_file_uploader:
    return None 
  if st.button("Back"):
    # Move to the previous state based on the current state
    if st.session_state.app_state == AppState.display_country_selector:
      st.session_state.app_state = AppState.display_file_uploader
    elif st.session_state.app_state == AppState.display_column_header_mapping:
      st.session_state.app_state = AppState.display_country_selector
    elif st.session_state.app_state == AppState.display_column_value_mapping:
      st.session_state.app_state = AppState.display_column_header_mapping
    elif st.session_state.app_state == AppState.display_column_default_value_selector:
      st.session_state.app_state = AppState.display_column_value_mapping
    elif st.session_state.app_state == AppState.display_download_import_sheet_button:
      st.session_state.app_state = AppState.display_column_default_value_selector

def app(llm_model):
  st.title("Talenox's import sheet mapper")
  initialise_session_state_variables()
  # Step 1: Upload file
  if st.session_state.app_state.value == AppState.display_file_uploader.value:
    render_upload_file_widget()
  # Step 2: Render country selector
  print(f"Start: {st.session_state.app_state}")
  if st.session_state.app_state.value == AppState.display_country_selector.value:
    # Step 2.1: Check that the file has been read correctly
    st.session_state.rows_to_skip = render_sheet_skiprow_widget()
    st.session_state.sampled_df, st.session_state.raw_data_headers = extract_header_and_sample_data(st.session_state.uploaded_file, st.session_state.rows_to_skip)
    st.session_state.user_sample_values = extract_unique_sample_values(st.session_state.uploaded_file, st.session_state.rows_to_skip, sheet_name=0)
    render_uploaded_file_head_widget(st.session_state.sampled_df)
    # Step 2.2: Choose country
    country = render_select_country_widget()
    render_confirm_country_button(country)
  print(f"End: {st.session_state.app_state}")
  # Step 3: Generate column header mappings
  if st.session_state.app_state.value == AppState.display_column_header_mapping.value:
    if st.session_state.previous_confirmed_country != st.session_state.confirmed_country:
      st.session_state.previous_confirmed_country = st.session_state.confirmed_country
      st.session_state['initial_mappings'] = None
    st.session_state.country_specific_tlx_import_sheet_headers = get_column_headers(st.session_state.confirmed_country.lower().replace(" ", "_"))
    initial_mappings = get_column_header_mappings(llm_model, st.session_state.raw_data_headers, st.session_state.user_sample_values, st.session_state.country_specific_tlx_import_sheet_headers)
    # Review proposed column header mappings by the LLM
    corrected_column_mappings = render_review_column_header_mapping_widget(initial_mappings, st.session_state.country_specific_tlx_import_sheet_headers)
    # Submit confirmed header mappings
    render_submit_column_header_mapping_button(corrected_column_mappings)
  # Step 4: Generate and value mappings
  if st.session_state.app_state.value == AppState.display_column_value_mapping.value:
    data = pd.read_excel(st.session_state.uploaded_file, skiprows=st.session_state.rows_to_skip)
    consolidated_accepted_column_values = get_tlx_column_dropdown_values(st.session_state.confirmed_country)
    generate_initial_fixed_column_value_mapping_widget(llm_model, consolidated_accepted_column_values, data)
    render_review_fixed_column_value_mapping_widget(st.session_state.corrected_column_mappings, consolidated_accepted_column_values, data)
    render_submit_fixed_column_value_mapping_button()
  # Step 5: Choose default values for mandatory columns
  if st.session_state.app_state.value == AppState.display_column_default_value_selector.value:
    render_choose_default_value_for_required_columns_widget()
    render_confirm_unmapped_column_default_values_button()
  # Step 6: Prepare file for download
  if st.session_state.app_state.value == AppState.display_download_import_sheet_button.value:
    render_final_import_sheet(st.session_state.uploaded_file, st.session_state.rows_to_skip, st.session_state.country_specific_tlx_import_sheet_headers)
    render_download_import_sheet_button()
  render_back_button()

if __name__ == "__main__":
  # st.session_state.clear()
  try:
    # Initialize the OpenAI client
    llm_model = OpenAi()
    
    # Initialize the Gemini client
    # llm_model = Gemini()
    app(llm_model)
  except Exception as e:
    # Catch any exception and handle it
    error_message = f"An error occurred: {str(e)}  \n"
    error_message += "\nPlease try again from the previous step."
    st.error(error_message)
