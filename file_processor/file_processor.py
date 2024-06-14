import pandas as pd
import streamlit as st
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import shutil

def get_uploaded_file():
  uploaded_file = st.file_uploader("Choose a file", type=["xlsx", "xls", "csv"])
  return uploaded_file

# Read the Excel file and sample rows of data
def read_excel_and_sample(filename, sheet_name=0, max_rows=10):
  # Read the entire Excel file
  df = pd.read_excel(filename, sheet_name=sheet_name, skiprows=2)
  # Extract the header rows
  headers = df.columns.tolist()
  # Sample a maximum of 10 rows
  sampled_df = df.sample(n=min(max_rows, len(df)), random_state=1)
  # Combine headers with sampled data
  result_df = pd.DataFrame(sampled_df, columns=headers)

  return result_df

# Read the Excel file and extract the header columns
def extract_headers_from_excel_file(filename, sheet_name=0):
  # Read the entire Excel file
  df = pd.read_excel(filename, sheet_name=sheet_name, skiprows=2)
  # Extract the header rows
  headers = df.columns.tolist()
  return headers

# Write to Excel file
def write_to_preformatted_excel(data, mappings, headers, country):
    # Load the preformatted Excel file
    template_path = f"tlx_import_sheet_samples/{country}.xlsx"
    temp_path = f"temp_{country}.xlsx"
    shutil.copy(template_path, temp_path)

    # Load the copied Excel file
    wb = load_workbook(temp_path)
    ws = wb.active
    # Create a DataFrame from the data
    df = pd.DataFrame(data)
    # Rename the columns based on mappings
    df = df.rename(columns=mappings)
    # Ensure all required headers are present, filling with empty strings if missing
    for header in headers:
        if header not in df.columns:
            df[header] = ''
    # Reorder columns to match the headers
    df = df[headers]
    # Write the DataFrame to the copied Excel file
    for row in dataframe_to_rows(df, index=False, header=False):
        ws.append(row)
    # Save the file
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    file_name = f"{country.lower()}.xlsx"
    st.download_button(
        label="Download Processed File",
        data=output,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Read CSV and sample rows of data
def read_csv_and_sample(filename, max_rows=10):
  # Read the entire CSV file
  df = pd.read_csv(filename)
  # Extract the header rows
  headers = df.columns.tolist()
  # Sample a maximum of 10 rows
  sampled_df = df.sample(n=min(max_rows, len(df)), random_state=1)
  # Combine headers with sampled data
  result_df = pd.DataFrame(sampled_df, columns=headers)
  return result_df

# Extract header columns from csv file
def extract_headers_from_csv(filename):
  # Read the entire CSV file
  df = pd.read_csv(filename)
  # Extract the header rows
  headers = df.columns.tolist()
  return headers

# Write column names and sample values to csv
def write_to_csv(result_df, output_path='sampled_output.csv'):
  result_df.to_csv(output_path, index=False)
    