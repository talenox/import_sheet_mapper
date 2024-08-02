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
from helper_methods.display_mappings import *
from helper_methods.normalise_string import *

# Load environment variables from .env file
load_dotenv()
# Suppress openpyxl warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

####################################################
COUNTRY_OPTIONS = ['SINGAPORE', 'MALAYSIA', 'HONG KONG', 'INDONESIA', 'GLOBAL']

def initialise_session_state_variables():
  if 'submit_column_header_mappings' not in st.session_state:
    st.session_state.submit_column_header_mappings = None
  if 'confirmed_country' not in st.session_state:
    st.session_state.confirmed_country = None
  if 'populate_import_sheet' not in st.session_state:
    st.session_state.populate_import_sheet = None
  if 'corrected_column_mappings' not in st.session_state:
    st.session_state.corrected_column_mappings = {}
  if 'download_import_sheet' not in st.session_state:
    st.session_state.download_import_sheet = False
  if 'previous_confirmed_country' not in st.session_state:
    st.session_state.previous_confirmed_country = None
  if 'column_header_name_normalised_mapping' not in st.session_state:
    st.session_state['column_header_name_normalised_mapping'] = {}
  if 'consolidated_corrected_value_mappings' not in st.session_state:
    st.session_state['consolidated_corrected_value_mappings'] = {}
  if 'mapped_data' not in st.session_state:
    st.session_state['mapped_data'] = pd.DataFrame()
  if 'unmapped_columns_default_values_confirmed' not in st.session_state:
    st.session_state['unmapped_columns_default_values_confirmed'] = False
  if 'submit_column_value_mapping' not in st.session_state:
    st.session_state['submit_column_value_mapping'] = False
  if 'column_header_name_normalised_mapping' not in st.session_state:
    st.session_state['column_header_name_normalised_mapping'] = {}

def render_upload_file_widget():
  st.subheader("Choose a file")
  return st.file_uploader("Upload the file containing your data.", type=["xlsx", "xls"])

def render_sheet_skiprow_widget():
    rows_to_skip = st.number_input("Enter the number of rows to skip. For example, if your data starts on the 3rd row, then input 2.", min_value=1, value=1)
    return rows_to_skip

def render_uploaded_file_head_widget(sampled_df):
  st.write("File Uploaded Successfully.")
  st.write(sampled_df)

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
    st.session_state['populate_import_sheet'] = None
    st.session_state['download_import_sheet'] = False
    st.session_state['submit_column_header_mappings'] = False
    st.session_state['column_header_name_normalised_mapping'] = load_column_header_name_normalised_mapping()

def get_column_header_mappings(llm_model, raw_data_headers, user_sample_values, country_specific_tlx_import_sheet_headers):
  country_specific_sample_values = get_sample_values(st.session_state.confirmed_country.lower().replace(" ", "_"))
  if st.session_state.initial_mappings is None:
    initial_mappings = generate_column_header_mappings(llm_model, raw_data_headers, user_sample_values, st.session_state['column_header_name_normalised_mapping'].values(), country_specific_sample_values)
    # initial_mappings = '''{
    #   "EmployeeCode": "Employee ID",
    #   "LastName": "Last Name*",
    #   "FirstName": "First Name*",
    #   "EmployeeName": {
    #     "column": "First Name*",
    #     "explanation": "Based on the context of mapping employee names"
    #   },
    #   "Gender": "Gender",
    #   "Title": "Job Title",
    #   "NationalityCode": "Nationality",
    #   "BirthDate": "Hired Date (DD/MM/YYYY)*",
    #   "RaceCode": "Race",
    #   "ReligionCode": "Religion",
    #   "MaritalStatus": "Marital Status",
    #   "Email": "Email",
    #   "BankAccountNo": "Bank Account No.",
    #   "BankBranch": "Bank Code",
    #   "BankCurrencyCode": {
    #     "column": "Currency of Salary",
    #     "explanation": "Based on the context of mapping currency"
    #   },
    #   "SFC01": "Nickname"
    # }
    # '''
    initial_mappings_cleaned = initial_mappings.replace('\n', '')
    initial_mappings_json = json.loads(initial_mappings_cleaned)
    st.session_state['initial_mappings'] = initial_mappings_json
  else:
    initial_mappings_json = st.session_state['initial_mappings']
  return initial_mappings_json

def render_review_column_header_mapping_widget(initial_mappings, country_specific_tlx_import_sheet_headers):
  st.header("Column Header Mappings")
  st.write("Please review and modify (if necessary) the proposed mappings:")
  corrected_column_mappings = display_initial_column_mappings(initial_mappings, "corrected_column_mappings")
  return corrected_column_mappings

def render_submit_column_header_mapping_button(corrected_column_mappings):
  if st.button("Submit Column Mappings"):
    st.session_state.submit_column_header_mappings = True
    st.write("Here are the confirmed column mappings.")
    with st.expander("Corrected Column Mappings:", expanded=False):
      st.write("", st.session_state.corrected_column_mappings)

def generate_initial_fixed_column_value_mapping_widget(llm_model, consolidated_accepted_column_values, data):
  for user_column, tlx_column in st.session_state.corrected_column_mappings.items():
    normalised_column_name = normalise_column_name(tlx_column)
    if normalised_column_name in consolidated_accepted_column_values:
      accepted_column_values = consolidated_accepted_column_values[normalised_column_name]
      # TODO Joshua remove this stub
      initial_value_mappings = generate_fixed_value_column_mappings(
        llm_model,
        data[user_column].unique().tolist(),
        accepted_column_values
      )
      st.session_state['consolidated_corrected_value_mappings'][normalised_column_name] = initial_value_mappings
  return None

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
    st.session_state.submit_column_value_mapping = True

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
    st.session_state.unmapped_columns_default_values_confirmed = True
  if st.session_state.unmapped_columns_default_values_confirmed:
    st.session_state.populate_import_sheet = True

def render_final_import_sheet(uploaded_file, rows_to_skip, country_specific_tlx_import_sheet_headers):
  # Read the uploaded file again to get the full data
  data = pd.read_excel(uploaded_file, skiprows=rows_to_skip, dtype="str")
  st.session_state.mapped_data = display_final_mapped_data(data, st.session_state.corrected_column_mappings, country_specific_tlx_import_sheet_headers[1:], st.session_state['consolidated_corrected_value_mappings'], st.session_state.confirmed_country)

def render_download_import_sheet_button():
  write_to_preformatted_excel(st.session_state.mapped_data, st.session_state.confirmed_country)

def app(llm_model):
  st.title("Talenox's import sheet mapper")
  initialise_session_state_variables()
  # Step 1: Upload file
  uploaded_file = render_upload_file_widget()
  # Step 2: Check that the file has been read correctly
  if uploaded_file is not None:
    rows_to_skip = render_sheet_skiprow_widget()
    sampled_df, raw_data_headers = extract_header_and_sample_data(uploaded_file, rows_to_skip)
    user_sample_values = extract_unique_sample_values(uploaded_file, rows_to_skip, sheet_name=0)
    render_uploaded_file_head_widget(sampled_df)
    # Step 3: Choose country
    country = render_select_country_widget()
    # Step 4: Confirm country
    render_confirm_country_button(country)
    # Step 5: Generate column header mappings
    if st.session_state.confirmed_country:
      if st.session_state.previous_confirmed_country != st.session_state.confirmed_country:
        st.session_state.previous_confirmed_country = st.session_state.confirmed_country
        st.session_state['initial_mappings'] = None
      country_specific_tlx_import_sheet_headers = get_column_headers(st.session_state.confirmed_country.lower().replace(" ", "_"))
      initial_mappings = get_column_header_mappings(llm_model, raw_data_headers, user_sample_values, country_specific_tlx_import_sheet_headers)
      # Step 6: Review proposed column header mappings by the LLM
      corrected_column_mappings = render_review_column_header_mapping_widget(initial_mappings, country_specific_tlx_import_sheet_headers)
      # Step 7: Submit confirmed header mappings
      render_submit_column_header_mapping_button(corrected_column_mappings)
      if st.session_state.submit_column_header_mappings:
        # Step 8: Generate and review value mapping based on column mappings
        data = pd.read_excel(uploaded_file, skiprows=rows_to_skip)
        consolidated_accepted_column_values = get_tlx_column_dropdown_values(st.session_state.confirmed_country)
        generate_initial_fixed_column_value_mapping_widget(llm_model, consolidated_accepted_column_values, data)
        render_review_fixed_column_value_mapping_widget(st.session_state.corrected_column_mappings, consolidated_accepted_column_values, data)
        render_submit_fixed_column_value_mapping_button()
        if st.session_state.submit_column_value_mapping:
          # Step 9: Choose default values for mandatory columns
          render_choose_default_value_for_required_columns_widget()
          render_confirm_unmapped_column_default_values_button()
          if st.session_state.populate_import_sheet:
            render_final_import_sheet(uploaded_file, rows_to_skip, country_specific_tlx_import_sheet_headers)
            render_download_import_sheet_button()
            

if __name__ == "__main__":
  # st.session_state.clear()
  # Initialize the OpenAI client
  llm_model = OpenAi()
  
  # Initialize the Gemini client
  # llm_model = Gemini()
  app(llm_model)
