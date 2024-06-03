from pandas import pd

# Read the Excel file and sample rows of data
def read_excel_file_data(file_path, sheet_name=0, max_rows=10):
  # Read the entire Excel file
  df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=1)
  # Extract the header rows
  headers = df.columns.tolist()
  # Sample a maximum of 10 rows
  sampled_df = df.sample(n=min(max_rows, len(df)), random_state=1)
  # Combine headers with sampled data
  result_df = pd.DataFrame(sampled_df, columns=headers)

  return result_df

# Read the Excel file and extract the header columns
def extract_headers_from_excel_file(file_path, sheet_name=0):
  # Read the entire Excel file
  df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=1)
  # Extract the header rows
  headers = df.columns.tolist()
  return headers

# Write to Excel file
def write_to_excel(result_df, output_path='sampled_output.xlsx'):
  with pd.ExcelWriter(output_path) as writer:
    result_df.to_excel(writer, index=False, sheet_name='Sheet1')

# Read CSV and sample rows of data
def read_csv_sample(file_path, max_rows=10):
  # Read the entire CSV file
  df = pd.read_csv(file_path)
  # Extract the header rows
  headers = df.columns.tolist()
  # Sample a maximum of 10 rows
  sampled_df = df.sample(n=min(max_rows, len(df)), random_state=1)
  # Combine headers with sampled data
  result_df = pd.DataFrame(sampled_df, columns=headers)
  return result_df

# Extract header columns from csv file
def extract_headers_from_csv(file_path):
  # Read the entire CSV file
  df = pd.read_csv(file_path)
  # Extract the header rows
  headers = df.columns.tolist()
  return headers

# Write column names and sample values to csv
def write_to_csv(result_df, output_path='sampled_output.csv'):
  result_df.to_csv(output_path, index=False)
    