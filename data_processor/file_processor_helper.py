import pandas as pd
import streamlit as st
import os
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import shutil
from tempfile import NamedTemporaryFile

# Read the Excel file and sample rows of data
def read_excel_and_sample(filename, rows_to_skip, sheet_name=0, max_rows=10):
  # Read the entire Excel file
  df = pd.read_excel(filename, sheet_name=sheet_name, skiprows=rows_to_skip, dtype=str)
  # Extract the header rows
  headers = df.columns.tolist()
  # Sample a maximum of 10 rows
  sampled_df = df.head(max_rows)
  # Combine headers with sampled data
  result_df = pd.DataFrame(sampled_df, columns=headers)

  return result_df

# Read the Excel file and extract the header columns
def extract_headers_from_excel_file(filename, rows_to_skip, sheet_name=0):
  # Read the entire Excel file
  df = pd.read_excel(filename, sheet_name=sheet_name, skiprows=rows_to_skip, dtype=str)
  # Extract the header rows
  headers = df.columns.tolist()
  return headers

# Write to Excel file
def write_to_preformatted_excel(data, country):
  try:
    # Load the workbook from the uploaded file
    uploaded_file = st.session_state.uploaded_tlx_file
    if uploaded_file is None:
      st.error("No file uploaded. Please upload a file first.")
      return
    # Load workbook
    wb = load_workbook(uploaded_file)
    headers = extract_headers_from_excel_file(uploaded_file, 2, sheet_name=0)  # Assuming 2 is the header row and 0 is the sheet index
    ws = wb.active
    # Reorder columns in DataFrame to match headers in Excel
    missing_headers = [header for header in headers if header not in data.columns]
    if missing_headers:
      raise ValueError(f"The following headers are missing in the DataFrame: {missing_headers}")
    data = data[headers]
    # Write DataFrame to the Excel sheet starting from the next empty row
    for row in dataframe_to_rows(data, index=False, header=False):
      ws.append(row)
    # Save workbook to a temporary file
    with NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
      temp_path = tmp.name
      wb.save(temp_path)
    # Prepare the file for download
    with open(temp_path, 'rb') as f:
      data = f.read()

    # Streamlit download button
    st.download_button(
      label="Download Import Sheet",
      data=data,
      file_name=f"{country.lower()}.xlsx",
      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

  except Exception as e:
    st.error(f"Error processing Excel file: {e}")

  finally:
    # Clean up temp file
    if 'temp_path' in locals() and os.path.exists(temp_path):
      os.remove(temp_path)

# Read CSV and sample rows of data
def read_csv_and_sample(filename, max_rows=10):
  # Read the entire CSV file
  df = pd.read_csv(filename, encoding='utf-8')
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
    