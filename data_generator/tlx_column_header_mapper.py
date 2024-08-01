import os
from datetime import datetime
import json
import csv
from data_processor.file_processor_helper import *

# This method generates new csv files containing header columns as a way of versioning
def update_column_headers(version):
  # Specify the source folder path containing the import sheets
  import_sheets_folder = "../import_sheet_mapper/data/tlx_import_sheet_samples"
  # Specify the folder path for the versioned column headers
  folder_path = f"../import_sheet_mapper/data/tlx_column_headers/{version}"
  # Create the folder if it doesn't exist
  if not os.path.exists(folder_path):
    os.makedirs(folder_path)
  # Iterate over the Excel files in the import sheets folder
  for file_name in os.listdir(import_sheets_folder):
    if file_name.endswith('.xlsx'):
      # Construct the full path to the Excel file
      excel_file_path = os.path.join(import_sheets_folder, file_name)   
      headers = extract_headers_from_excel_file(excel_file_path, 2, sheet_name=0)
      # Construct the output CSV file path
      csv_file_name = os.path.splitext(file_name)[0] + '_column_headers.csv'
      output_csv_path = os.path.join(folder_path, csv_file_name)
      # Write the headers to the CSV file
      with open(output_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
 
def get_latest_directory_path(base_dir):
  """Get the path to the latest directory based on date."""
  # Get a list of directories (dates)
  dates = [entry for entry in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, entry))]
  # Parse dates into datetime objects and identify the latest date
  parsed_dates = [datetime.strptime(date, "%Y-%m-%d") for date in dates]
  latest_date = max(parsed_dates)
  # Return the path to the latest directory
  return os.path.join(base_dir, latest_date.strftime("%Y-%m-%d"))

def load_json_file(filepath):
  """Load a JSON file if it exists."""
  if os.path.isfile(filepath):
    with open(filepath, 'r') as file:
      return json.load(file)
  else:
    print(f"File not found: {filepath}")
    return {}

def get_column_headers(country="singapore"):
  base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/tlx_column_headers')
  latest_contents_path = get_latest_directory_path(base_dir)
  target_file = os.path.join(latest_contents_path, country, "column_headers.csv")

  if os.path.isfile(target_file):
    with open(target_file, 'r') as file:
      return file.read().split(',')
  else:
    return f"{country}.csv not found in {latest_contents_path}"

def get_tlx_column_dropdown_values(country="singapore"):
  base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/tlx_column_headers')
  latest_contents_path = get_latest_directory_path(base_dir)
  
  shared_data = load_json_file(os.path.join(latest_contents_path, "shared_column_dropdown_values.json"))
  country_data = load_json_file(os.path.join(latest_contents_path, country, "column_dropdown_values.json"))
  
  # Combine the two dictionaries
  combined_data = {**shared_data, **country_data}
  return combined_data

def get_sample_values(country="singapore"):
  base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/tlx_column_headers')
  latest_contents_path = get_latest_directory_path(base_dir)
  target_file = os.path.join(latest_contents_path, country, 'sample_data.json')
  
  if os.path.isfile(target_file):
    with open(target_file, 'r') as file:
      json_contents = json.load(file)
      return json.dumps(json_contents, ensure_ascii=False, indent=2)
  else:
    return f"{country}.json not found in {latest_contents_path}"
  
def get_mandatory_columns(country="singapore"):
  base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/tlx_column_headers')
  latest_contents_path = get_latest_directory_path(base_dir)
  target_file = os.path.join(latest_contents_path, country, 'mandatory_fixed_value_columns.txt')
  
  if os.path.isfile(target_file):
    with open(target_file, 'r') as file:
      mandatory_columns = file.read().splitlines()
      return mandatory_columns
  else:
    return f"Not found in {latest_contents_path}"
  
def load_column_header_name_normalised_mapping():
  # Get the confirmed country from session state
  confirmed_country = st.session_state.confirmed_country
  if confirmed_country:
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/tlx_column_headers')
    latest_contents_path = get_latest_directory_path(base_dir)
    target_file = os.path.join(latest_contents_path, confirmed_country, 'normalized_column_headers.json')

    if os.path.isfile(target_file):
      # Load the JSON data
      with open(target_file, 'r') as jsonfile:
        return json.load(jsonfile)
    else:
      raise FileNotFoundError(f"File not found: {target_file}")
  else:
    raise ValueError("No confirmed country in session state.")