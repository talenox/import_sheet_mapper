from data_processor.file_processor_helper import *
from datetime import datetime
import json

# This method extracts a list of header column names and some sample data for display purposes
def extract_header_and_sample_data(uploaded_file, rows_to_skip):
  if uploaded_file.name.endswith('.csv'):
      sampled_df = read_csv_and_sample(uploaded_file)
      raw_data_headers = extract_headers_from_csv(uploaded_file)
  else:
    sampled_df = read_excel_and_sample(uploaded_file, rows_to_skip)
    raw_data_headers = extract_headers_from_excel_file(uploaded_file, rows_to_skip)
  
  return sampled_df, raw_data_headers

# This method extracts unique values for each column in the sheet and packs it up into a json to feed into the LLM prompt
def extract_unique_sample_values(uploaded_file, rows_to_skip, sheet_name=0):
  df = pd.read_excel(uploaded_file, sheet_name=sheet_name, skiprows=rows_to_skip)
  # Initialize dictionary to store sampled data lists
  sampled_data = {}

  # Iterate over columns in the DataFrame
  for col in df.columns:
    # Get unique non-NaN values from the column
    unique_values = df[col].dropna().unique()[:2].tolist()
    # Add to sampled_data if there are unique values
    if unique_values:
      sampled_data[col] = unique_values

  # Convert dictionary to JSON string with 2-space indentation
  try:
    sample_data = json.dumps(sampled_data, ensure_ascii=False, indent=2, default=datetime_serializer)
  except TypeError as e:
    st.error(f"Failed to encode JSON: {e}")
  
  return sample_data

# This method serializes datetime objects to strings 
def datetime_serializer(obj):
  if isinstance(obj, datetime):
    return obj.isoformat()
  raise TypeError(f"Type {type(obj)} not serializable")
