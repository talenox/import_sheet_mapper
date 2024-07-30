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
  latest_contents_path = os.path.join(directory_path, latest_directory, country)

  # Define the path to the target CSV file
  target_file = os.path.join(latest_contents_path, "column_headers.csv")

  # Check if the target file exists and print its contents
  if os.path.isfile(target_file):
    with open(target_file, 'r') as file:
      file_contents = file.read().split(',')
      return(file_contents)
  else:
    return(f"{country}.csv not found in {latest_contents_path}")

def get_tlx_column_dropdown_values():
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
  target_file = os.path.join(latest_contents_path, "shared_column_dropdown_values.json")
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