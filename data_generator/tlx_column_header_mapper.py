import os
from datetime import datetime
import json

# We maintain a list of column headers for each country supported by our import sheet
SINGAPORE_COLUMN_HEADERS = [
 "Employee ID",
 "First Name",
 "Last Name",
 "Nickname",
 "Chinese Name",
 "Email",
 "Invite User",
 "User Email (if different from employee email)",
 "User UID (for SSO purposes)",
 "User Provider (for SSO purposes)",
 "Override User (for SSO purposes)",
 "Access Role",
 "My Profile Module",
 "Payslip Module",
 "Tax Module",
 "Leave Module",
 "Payroll Module",
 "Profile Module",
 "Claims Module (User)",
 "Claims Module (Admin)",
 "Birth Date (DD/MM/YYYY)",
 "Gender",
 "Marital Status",
 "Identification No",
 "Immigration Status",
 "PR Status",
 "PR Effective Date (DD/MM/YYYY)",
 "PR Expiry Date (DD/MM/YYYY)",
 "S Pass Issue Date (DD/MM/YYYY)",
 "S Pass Expiry Date (DD/MM/YYYY)",
 "S Pass Dependency Ceiling",
 "E Pass Issue Date (DD/MM/YYYY)",
 "E Pass Expiry Date (DD/MM/YYYY)",
 "Letter of Consent Issue Date (DD/MM/YYYY)",
 "Letter of Consent Expiry Date (DD/MM/YYYY)",
 "Personalised Employment Pass Issue Date (DD/MM/YYYY)",
 "Personalised Employment Pass Expiry Date (DD/MM/YYYY)",
 "Work Pass Number",
 "Work Pass Issue Date (DD/MM/YYYY)",
 "Work Pass Expiry Date (DD/MM/YYYY)",
 "Work Pass Dependency Ceiling",
 "Work Pass Worker Category",
 "Tech Pass Issue Date (DD/MM/YYYY)",
 "Tech Pass Expiry Date (DD/MM/YYYY)",
 "ONE Pass Issue Date (DD/MM/YYYY)",
 "ONE Pass Expiry Date (DD/MM/YYYY)",
 "Training Employment Pass Issue Date (DD/MM/YYYY)",
 "Training Employment Pass Expiry Date (DD/MM/YYYY)",
 "Training Work Permit Issue Date (DD/MM/YYYY)",
 "Training Work Permit Expiry Date (DD/MM/YYYY)",
 "Identification Issue Date (DD/MM/YYYY)",
 "Identification Expiry Date (DD/MM/YYYY)",
 "Passport No.",
 "Passport Date of Issue (DD/MM/YYYY)",
 "Passport Date of Expiry (DD/MM/YYYY)",
 "Passport Place of Issue",
 "Nationality",
 "Race",
 "Religion",
 "Job Title",
 "Hired Date (DD/MM/YYYY)",
 "Is a rehire",
 "Rehiring Reason",
 "Job Start Date (DD/MM/YYYY)",
 "Job End Date (DD/MM/YYYY)",
 "Department",
 "Location/Branch",
 "Default Cost Centre",
 "Default Cost Centre Override",
 "Role",
 "Confirmation Date (DD/MM/YYYY)",
 "Working Day",
 "Working Hour",
 "Rate of Pay",
 "Currency of Salary",
 "Basic Salary",
 "Designation in Accounting Software",
 "Job Remarks",
 "Resign Date (DD/MM/YYYY)",
 "Resignation Reason",
 "Payment Method",
 "Bank Type",
 "Bank Account Holder's Name",
 "Bank Account No.",
 "Bank Branch No.",
 "Automatically calculate SHG",
 "SHG Contribution",
 "Additional SHG Contribution",
 "CPF in lieu",
 "Contact Number",
 "Office Direct Inward Dialing (DID) Number",
 "Address Line 1",
 "Address Line 2",
 "Country",
 "Region",
 "Subregion",
 "Postal Code",
 "Next of Kin's Name",
 "Next of Kin's Nationality",
 "Next of Kin's Gender",
 "Next of Kin's Birth Date (DD/MM/YYYY)",
 "Next of Kin's Identification No.",
 "Next of Kin's Passport No.",
 "Next of Kin's Relationship",
 "Next of Kin's Marriage Date (Spouse) (DD/MM/YYYY)",
 "Next of Kin's Contact No.",
 "Covid-19 Vaccination Status",
 "Covid-19 Vaccine Brand",
 "Date of 1st Dose (DD/MM/YYYY)",
 "Date of 2nd Dose (DD/MM/YYYY)",
 "Covid-19 Vaccine Booster Brand",
 "Date of Booster Dose (DD/MM/YYYY)",
 "Vaccination Remarks",
 "Halal Certification Issue Date (DD/MM/YYYY)",
 "Halal Certification Expiry Date (DD/MM/YYYY)",
 "Hygiene Certification Issue Date (DD/MM/YYYY)",
 "Hygiene Certification Expiry Date (DD/MM/YYYY)",
 "Custom Fields Hash",
 "Overwrite Jobs Array (Ignore current jobs columns)"
]

HONG_KONG_COLUMN_HEADERS = [
 "Employee ID",
 "First Name",
 "Last Name",
 "Nickname",
 "Chinese Name",
 "Email",
 "Invite User",
 "User Email (if different from employee email)",
 "Access Role",
 "My Profile Module",
 "Payslip Module",
 "Tax Module",
 "Leave Module",
 "Payroll Module",
 "Profile Module",
 "Claims Module (User)",
 "Claims Module (Admin)",
 "Birth Date (DD/MM/YYYY)",
 "Gender",
 "Marital Status",
 "HKID Number",
 "Visa Type",
 "MPF Member Account Number",
 "MPF Scheme",
 "MPF Employee Type",
 "MPF Voluntary Employee Additional Contribution Type",
 "MPF Voluntary Employee Additional Amount",
 "MPF Voluntary Employee Additional Rate",
 "MPF Voluntary Employer Additional Contribution Type",
 "MPF Voluntary Employer Additional Amount",
 "MPF Voluntary Employer Additional Rate",
 "Passport No.",
 "Passport Date of Issue (DD/MM/YYYY)",
 "Passport Date of Expiry (DD/MM/YYYY)",
 "Passport Place of Issue",
 "Nationality",
 "Race",
 "Religion",
 "Job Title",
 "Hired Date (DD/MM/YYYY)",
 "Job Start Date (DD/MM/YYYY)",
 "Department",
 "Location/Branch",
 "Default Cost Centre",
 "Role",
 "Confirmation Date (DD/MM/YYYY)",
 "Working Day",
 "Working Hour",
 "Rate of Pay",
 "Currency of Salary",
 "Basic Salary",
 "Designation in Accounting Software",
 "Job Remarks",
 "Resign Date (DD/MM/YYYY)",
 "Payment Method",
 "Bank Type",
 "Bank Account Holder's Name",
 "Bank Account No.",
 "Bank Branch No.",
 "Contact Number",
 "Office Direct Inward Dialing (DID) Number",
 "Address Line 1",
 "Address Line 2",
 "Country",
 "Region",
 "Subregion",
 "Postal Code",
 "Next of Kin's Name",
 "Next of Kin's Nationality",
 "Next of Kin's Gender",
 "Next of Kin's Birth Date (DD/MM/YYYY)",
 "Next of Kin's Identification No.",
 "Next of Kin's Passport No.",
 "Next of Kin's Relationship",
 "Next of Kin's Marriage Date (Spouse) (DD/MM/YYYY)",
 "Next of Kin's Contact No.",
 "Covid-19 Vaccination Status",
 "Covid-19 Vaccine Brand",
 "Date of 1st Dose (DD/MM/YYYY)",
 "Date of 2nd Dose (DD/MM/YYYY)",
 "Covid-19 Vaccine Booster Brand",
 "Date of Booster Dose (DD/MM/YYYY)",
 "Vaccination Remarks"
]

MALAYSIA_COLUMN_HEADERS = [
 "Employee ID",
 "First Name",
 "Last Name",
 "Nickname",
 "Chinese Name",
 "Email",
 "Invite User",
 "User Email (if different from employee email)",
 "Access Role",
 "My Profile Module",
 "Payslip Module",
 "Tax Module",
 "Leave Module",
 "Payroll Module",
 "Profile Module",
 "Claims Module (User)",
 "Claims Module (Admin)",
 "Birth Date (DD/MM/YYYY)",
 "Gender",
 "Marital Status",
 "Identification Number",
 "Immigration Status",
 "Disabled Individual",
 "Disabled Spouse",
 "Contributing EPF?",
 "EPF Number",
 "Employee EPF Setting",
 "Employer EPF Setting",
 "PCB No(Income tax no)",
 "PCB Borne by Employer",
 "Socso Category",
 "Employment Insurance System(EIS)",
 "Zakat No.",
 "Zakat Amount",
 "Contributing HRDF?",
 "Passport No.",
 "Passport Date of Issue (DD/MM/YYYY)",
 "Passport Date of Expiry (DD/MM/YYYY)",
 "Passport Place of Issue",
 "Nationality",
 "Race",
 "Religion",
 "Job Title",
 "Hired Date (DD/MM/YYYY)",
 "Job Start Date (DD/MM/YYYY)",
 "Department",
 "Location/Branch",
 "Default Cost Centre",
 "Role",
 "Confirmation Date (DD/MM/YYYY)",
 "Working Day",
 "Working Hour",
 "Rate of Pay",
 "Currency of Salary",
 "Basic Salary",
 "Designation in Accounting Software",
 "Job Remarks",
 "Resign Date (DD/MM/YYYY)",
 "Payment Method",
 "Bank Type",
 "Bank Account Holder's Name",
 "Bank Account No.",
 "Contact Number",
 "Office Direct Inward Dialing (DID) Number",
 "Address Line 1",
 "Address Line 2",
 "Country",
 "Region",
 "Subregion",
 "Postal Code",
 "Next of Kin's Name",
 "Next of Kin's Nationality",
 "Next of Kin's Gender",
 "Next of Kin's Birth Date (DD/MM/YYYY)",
 "Next of Kin's Identification No.",
 "Next of Kin's Passport No.",
 "Next of Kin's Relationship",
 "Next of Kin's Marriage Date (Spouse) (DD/MM/YYYY)",
 "Next of Kin's Contact No.",
 "Children Claimed Under 18 Full Deduction",
 "Children Claimed Under 18 Half Deduction",
 "Children Claimed Over 18 Studying including Marriage Full Deduction",
 "Children Claimed Over 18 Studying including Marriage Half Deduction",
 "Children Claimed Over 18 Studying Diploma Full Time Full Deduction",
 "Children Claimed Over 18 Studying Diploma Full Time Half Deduction",
 "Children Claimed Disabled Full Deduction",
 "Children Claimed Disabled Half Deduction",
 "Children Claimed Disabled Studying Diploma Full Deduction",
 "Children Claimed Disabled Studying Diploma Half Deduction",
 "Accumulated remuneration/Benefit-In-Kind (BIK)/Value Of Living Accomodation (VOLA)",
 "Accumulated EPF and Other Approved Funds [include life premium insurance]",
 "Accumulated MTD paid (including MTD on additional remuneration)",
 "Accumulated SOCSO Contribution",
 "Accumulated Zakat paid",
 "Payroll year to start applying accumulated deductions.",
 "Payroll month to start applying accumulated deductions.",
 "Covid-19 Vaccination Status",
 "Covid-19 Vaccine Brand",
 "Date of 1st Dose (DD/MM/YYYY)",
 "Date of 2nd Dose (DD/MM/YYYY)",
 "Covid-19 Vaccine Booster Brand",
 "Date of Booster Dose (DD/MM/YYYY)",
 "Vaccination Remarks"
]

GLOBAL_COLUMN_HEADERS = [
 "Employee ID",
 "First Name",
 "Last Name",
 "Nickname",
 "Chinese Name",
 "Email",
 "Invite User",
 "User Email (if different from employee email)",
 "Access Role",
 "My Profile Module",
 "Payslip Module",
 "Leave Module",
 "Payroll Module",
 "Profile Module",
 "Claims Module (User)",
 "Claims Module (Admin)",
 "Birth Date (DD/MM/YYYY)",
 "Gender",
 "Marital Status",
 "Identification Number",
 "Passport No.",
 "Passport Date of Issue (DD/MM/YYYY)",
 "Passport Date of Expiry (DD/MM/YYYY)",
 "Passport Place of Issue",
 "Nationality",
 "Job Title",
 "Hired Date (DD/MM/YYYY)",
 "Race",
 "Religion",
 "Job Start Date (DD/MM/YYYY)",
 "Department",
 "Location/Branch",
 "Default Cost Centre",
 "Role",
 "Confirmation Date (DD/MM/YYYY)",
 "Working Day",
 "Working Hour",
 "Rate of Pay",
 "Currency of Salary",
 "Basic Salary",
 "Designation in Accounting Software",
 "Job Remarks",
 "Resign Date (DD/MM/YYYY)",
 "Payment Method",
 "Bank Type",
 "Bank Account Holder's Name",
 "Bank Account No.",
 "Contact Number",
 "Office Direct Inward Dialing (DID) Number",
 "Address Line 1",
 "Address Line 2",
 "Country",
 "Region",
 "Subregion",
 "Postal Code",
 "Next of Kin's Name",
 "Next of Kin's Nationality",
 "Next of Kin's Gender",
 "Next of Kin's Birth (DD/MM/YYYY) Date",
 "Next of Kin's Identification No.",
 "Next of Kin's Passport No.",
 "Next of Kin's Relationship",
 "Next of Kin's Marriage Date (Spouse) (DD/MM/YYYY)",
 "Next of Kin's Contact No.",
 "Covid-19 Vaccination Status",
 "Covid-19 Vaccine Brand",
 "Date of 1st Dose (DD/MM/YYYY)",
 "Date of 2nd Dose (DD/MM/YYYY)",
 "Covid-19 Vaccine Booster Brand",
 "Date of Booster Dose (DD/MM/YYYY)",
 "Vaccination Remarks"
]

INDONESIA_COLUMN_HEADERS = [
 "Employee ID",
 "First Name",
 "Last Name",
 "Nickname",
 "Email",
 "Invite User",
 "User Email (if different from employee email)",
 "Access Role",
 "My Profile Module",
 "Payslip Module",
 "Leave Module",
 "Payroll Module",
 "Profile Module",
 "Claims Module (User)",
 "Claims Module (Admin)",
 "Birth Date (DD/MM/YYYY)",
 "Gender",
 "Marital Status",
 "Immigration Status",
 "Identification Number",
 "Blood Group",
 "Passport No.",
 "Passport Date of Issue (DD/MM/YYYY)",
 "Passport Date of Expiry (DD/MM/YYYY)",
 "Passport Place of Issue",
 "Nationality",
 "Race",
 "Religion",
 "Job Title",
 "Hired Date (DD/MM/YYYY)",
 "Job Start Date (DD/MM/YYYY)",
 "Department",
 "Location/Branch",
 "Default Cost Centre",
 "Role",
 "Confirmation Date (DD/MM/YYYY)",
 "Working Day",
 "Working Hour",
 "Rate of Pay",
 "Currency of Salary",
 "Basic Salary",
 "Designation in Accounting Software",
 "Job Remarks",
 "Resign Date (DD/MM/YYYY)",
 "Payment Method",
 "Bank Type",
 "Bank Account Holder's Name",
 "Bank Account No.",
 "Contact Number",
 "Office Direct Inward Dialing (DID) Number",
 "Address Line 1",
 "Address Line 2",
 "Country",
 "Province",
 "County",
 "Postal Code",
 "Next of Kin's Name",
 "Next of Kin's Nationality",
 "Next of Kin's Gender",
 "Next of Kin's Birth Date (DD/MM/YYYY)",
 "Next of Kin's Identification No.",
 "Next of Kin's Passport No.",
 "Next of Kin's Relationship",
 "Next of Kin's Marriage Date (Spouse) (DD/MM/YYYY)",
 "Next of Kin's Contact No.",
 "Tax Processing Date (DD/MM/YYYY)",
 "PTKP",
 "NPWP",
 "Tax Scheme",
 "Previous Past Net & Tax Effective Date (DD/MM/YYYY)",
 "Previous Past Net",
 "Previous Past Tax",
 "BPJS TK Process Date (DD/MM/YYYY)",
 "BPJS TK Number",
 "BPJS JKK Policy",
 "BPJS JKK Contribution Rate",
 "BPJS JKM Policy",
 "BPJS JP Policy",
 "BPJS JP Borne by Employer",
 "BPJS JHT Policy",
 "BPJS JHT Borne by Employer",
 "BPJS Kesehatan Process Date (DD/MM/YYYY)",
 "BPJS Kesehatan Number",
 "BPJS Kesehatan Policy",
 "BPJS Kesehatan No of Dependants",
 "BPJS Kesehatan Borne by Employer",
 "Covid-19 Vaccination Status",
 "Covid-19 Vaccine Brand",
 "Date of 1st Dose (DD/MM/YYYY)",
 "Date of 2nd Dose (DD/MM/YYYY)",
 "Covid-19 Vaccine Booster Brand",
 "Date of Booster Dose (DD/MM/YYYY)",
 "Vaccination Remarks"
]

# Write all the header columns to a csv file
FILE_NAME_MAPPING_DICT = {
  "singapore": SINGAPORE_COLUMN_HEADERS,
  "hong_kong": HONG_KONG_COLUMN_HEADERS,
  "malaysia": MALAYSIA_COLUMN_HEADERS,
  "global": GLOBAL_COLUMN_HEADERS,
  "indonesia": INDONESIA_COLUMN_HEADERS
}

# This method generates new csv files containing header columns as a way of versioning
def update_column_headers(version):
  # Specify the folder path
  folder_path = f"../tlx_column_headers/{version}"

  # Create the folder if it doesn't exist
  if not os.path.exists(folder_path):
    os.makedirs(folder_path)

  # Iterate over the dictionary and write to CSV files in the specified folder
  for key, column_headers in FILE_NAME_MAPPING_DICT.items():
    file_name = os.path.join(folder_path, f"{key}.csv")
    with open(file_name, 'w', newline='') as csvfile:
      writer = csv.writer(csvfile)
      writer.writerow(column_headers)

def get_column_headers(country="singapore"):
  # Define the directory path relative to this script's location
  script_dir = os.path.dirname(os.path.abspath(__file__))
  directory_path = os.path.join(script_dir, '../data/tlx_column_headers')
  # Get a list of directories (dates)
  dates = [entry for entry in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, entry))]
  # Parse dates into datetime objects
  parsed_dates = [datetime.strptime(date, "%Y-%m-%d") for date in dates]
  # Identify the latest date
  latest_date = max(parsed_dates)
  # Find the directory corresponding to the latest date
  latest_directory = latest_date.strftime("%Y-%m-%d")

  # Access the contents of the latest directory
  latest_contents_path = os.path.join(directory_path, latest_directory)

  # Define the path to the target CSV file
  target_file = os.path.join(latest_contents_path, f"{country}.csv")

  # Check if the target file exists and print its contents
  if os.path.isfile(target_file):
    with open(target_file, 'r') as file:
      file_contents = file.read().split(',')
      return(file_contents)
  else:
    return(f"{country}.csv not found in {latest_contents_path}")

def get_column_dropdown_values():
  # Define the directory path relative to this script's location
  script_dir = os.path.dirname(os.path.abspath(__file__))
  directory_path = os.path.join(script_dir, '../data/tlx_column_headers')
  # Get a list of directories (dates)
  dates = [entry for entry in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, entry))]
  # Parse dates into datetime objects
  parsed_dates = [datetime.strptime(date, "%Y-%m-%d") for date in dates]
  # Identify the latest date
  latest_date = max(parsed_dates)
  # Find the directory corresponding to the latest date
  latest_directory = latest_date.strftime("%Y-%m-%d")
  # Access the contents of the latest directory
  latest_contents_path = os.path.join(directory_path, latest_directory)
  # Define the path to the target CSV file
  target_file = os.path.join(latest_contents_path, "column_dropdown_values.json")
  # Check if the target file exists and print its contents
  if os.path.isfile(target_file):
    with open(target_file, 'r') as file:
      data = json.load(file)
      return data
  else:
    return f"File not found in {latest_contents_path}"

def get_sample_values(country="singapore"):
  # Define the directory path relative to this script's location
  script_dir = os.path.dirname(os.path.abspath(__file__))
  directory_path = os.path.join(script_dir, '../data/tlx_column_headers')
  
  # Get a list of directories (dates)
  dates = [entry for entry in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, entry))]
  
  # Parse dates into datetime objects
  parsed_dates = [datetime.strptime(date, "%Y-%m-%d") for date in dates]
  
  # Identify the latest date
  latest_date = max(parsed_dates)
  
  # Find the directory corresponding to the latest date
  latest_directory = latest_date.strftime("%Y-%m-%d")
  
  # Access the contents of the latest directory
  latest_contents_path = os.path.join(directory_path, latest_directory)
  
  # Define the path to the target JSON file
  target_file = os.path.join(latest_contents_path, f"{country}_sample_data.json")
  
  # Check if the target file exists and load its contents
  if os.path.isfile(target_file):
    with open(target_file, 'r') as file:
      json_contents = json.load(file)
      return json.dumps(json_contents, ensure_ascii=False, indent=2)
  else:
    return f"{country}.json not found in {latest_contents_path}"