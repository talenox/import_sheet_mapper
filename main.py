from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import streamlit as st
import warnings
from llm_mapper.openai import OpenAiMapper
from file_processor.file_processor import *
from static_data_generator.tlx_column_header_mapper import *

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
  raise ValueError("OpenAI API key is not set. Please check your .env file.")

# Suppress openpyxl warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

####################################################
COUNTRY_OPTIONS = ['SINGAPORE', 'MALAYSIA', 'HONG KONG', 'INDONESIA', 'GLOBAL']

def extract_file_data(uploaded_file):
  if uploaded_file.name.endswith('.csv'):
      sampled_df = read_csv_and_sample(uploaded_file)
      raw_data_headers = extract_headers_from_csv(uploaded_file)
  else:
    sampled_df = read_excel_and_sample(uploaded_file)
    raw_data_headers = extract_headers_from_excel_file(uploaded_file)
  return sampled_df, raw_data_headers

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

def display_initial_mappings(initial_mappings_json, country_specific_tlx_import_sheet_headers):
  if 'corrected_mappings' not in st.session_state:
    st.session_state.corrected_mappings = {}

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
      corrected = st.selectbox(f"Predefined Header for '{user_header}':", country_specific_tlx_import_sheet_headers, index=initial_index,key=user_header)
      key += 1
    st.session_state.corrected_mappings[user_header_input] = corrected
  return st.session_state.corrected_mappings

def app():
  st.title("Upload and Process Excel/CSV File")
  uploaded_file = get_uploaded_file()
  if uploaded_file is not None:
    sampled_df, raw_data_headers = extract_file_data(uploaded_file)
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
      initial_mappings = generate_mappings(raw_data_headers, country_specific_tlx_import_sheet_headers)
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
      #     "Birth Date (DD/MM/YYYY)*": "Birth Date (DD/MM/YYYY)",
      #     "Gender": "Gender",
      #     "Marital Status*": "Marital Status",
      #     "Identification Number*": "Identification No",
      #     "Immigration Status*": "Immigration Status",
      #     "Disabled Individual*": "N/A (Suggestion: Include the column as needed)",
      #     "Disabled Spouse*": "N/A (Suggestion: Include the column as needed)",
      #     "Contributing EPF?*": "N/A (Suggestion: Include the column as needed)",
      #     "EPF Number*": "N/A (Suggestion: Include the column as needed)",
      #     "Employee EPF Setting*": "N/A (Suggestion: Include the column as needed)",
      #     "Employer EPF Setting*": "N/A (Suggestion: Include the column as needed)",
      #     "PCB No.(Income tax no.)*": "N/A (Suggestion: Include the column as needed)",
      #     "PCB Borne by Employer*": "N/A (Suggestion: Include the column as needed)",
      #     "Socso Category*": "N/A (Suggestion: Include the column as needed)",
      #     "Employment Insurance System(EIS)*": "N/A (Suggestion: Include the column as needed)",
      #     "Zakat No.": "N/A (Suggestion: Include the column as needed)",
      #     "Zakat Amount": "N/A (Suggestion: Include the column as needed)",
      #     "Contributing HRDF?*": "N/A (Suggestion: Include the column as needed)",
      #     "Passport No": "Passport No.",
      #     "Passport Date of Issue (DD/MM/YYYY)": "Passport Date of Issue (DD/MM/YYYY)",
      #     "Passport Date of Expiry (DD/MM/YYYY)": "Passport Date of Expiry (DD/MM/YYYY)",
      #     "Passport Place of Issue": "Passport Place of Issue",
      #     "Nationality": "Nationality",
      #     "Race": "Race",
      #     "Religion": "Religion",
      #     "Job Title*": "Job Title",
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
      #     "Contact Number": "Contact Number",
      #     "Office Direct Inward Dialing (DID) Number": "Office Direct Inward Dialing (DID) Number",
      #     "Address Line 1": "Address Line 1",
      #     "Address Line 2": "Address Line 2",
      #     "Country": "Country",
      #     "Region": "Region",
      #     "Subregion": "Subregion",
      #     "Postal Code": "Postal Code",
      #     "Next of Kins Name": "Next of Kin's Name",
      #     "Next of Kins Nationality": "Next of Kin's Nationality",
      #     "Next of Kins Gender": "Next of Kin's Gender",
      #     "Next of Kins Birth Date (DD/MM/YYYY)": "Next of Kin's Birth Date (DD/MM/YYYY)",
      #     "Next of Kins Identification No.": "Next of Kin's Identification No.",
      #     "Next of Kins Passport No.": "Next of Kin's Passport No.",
      #     "Next of Kins Relationship": "Next of Kin's Relationship",
      #     "Next of Kins Marriage Date (Spouse) (DD/MM/YYYY)": "Next of Kin's Marriage Date (Spouse) (DD/MM/YYYY)",
      #     "Next of Kins Contact No.": "Next of Kin's Contact No.",
      #     "Accumulated remuneration/Benefit-In-Kind (BIK)/Value Of Living Accomodation (VOLA)*": "N/A (Suggestion: Include the column as needed)",
      #     "Accumulated EPF and Other Approved Funds [include life premium insurance]*": "N/A (Suggestion: Include the column as needed)",
      #     "Accumulated MTD paid (including MTD on additional remuneration)*": "N/A (Suggestion: Include the column as needed)",
      #     "Accumulated SOCSO Contribution*": "N/A (Suggestion: Include the column as needed)",
      #     "Accumulated Zakat paid*": "N/A (Suggestion: Include the column as needed)",
      #     "Payroll year to start applying accumulated deductions.*": "N/A (Suggestion: Include the column as needed)",
      #     "Payroll month to start applying accumulated deductions.*": "N/A (Suggestion: Include the column as needed)",
      #     "Covid-19 Vaccination Status": "Covid-19 Vaccination Status",
      #     "Covid-19 Vaccine Brand": "Covid-19 Vaccine Brand",
      #     "Date of 1st Dose (DD/MM/YYYY)": "Date of 1st Dose (DD/MM/YYYY)",
      #     "Date of 2nd Dose (DD/MM/YYYY)": "Date of 2nd Dose (DD/MM/YYYY)",
      #     "Covid-19 Vaccine Booster Brand": "Covid-19 Vaccine Booster Brand",
      #     "Date of Booster Dose (DD/MM/YYYY)": "Date of Booster Dose (DD/MM/YYYY)",
      #     "Vaccination Remarks": "Vaccination Remarks",
      #     "Unnamed: 91": "N/A (Suggestion: Include the column as needed)"
      #   }
      # '''
      initial_mappings_cleaned = initial_mappings.replace('\n', '')
      initial_mappings_json = json.loads(initial_mappings_cleaned)
      st.write("Please review and correct the mappings:")
      corrected_mappings = display_initial_mappings(initial_mappings_json, country_specific_tlx_import_sheet_headers)

      if st.button("Submit Mappings"):
        st.write("Final Corrected Mappings:", corrected_mappings)
        # Read the uploaded file again to get the full data
        data = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)

        # Write to the preformatted file
        write_to_preformatted_excel(data, corrected_mappings, country_specific_tlx_import_sheet_headers[1:], st.session_state.confirmed_country)

if __name__ == "__main__":
  app()