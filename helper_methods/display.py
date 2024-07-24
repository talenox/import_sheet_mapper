import json
import re
import streamlit as st
from data_processor.extractor import *
from data_generator.tlx_column_header_mapper import *
from helper_methods.mapper import *

# This method displays the initial mappings done by the LLM on the UI
def display_initial_mappings(initial_mappings_json, country_specific_tlx_import_sheet_headers):
  if 'corrected_mappings' not in st.session_state:
    st.session_state.corrected_mappings = {}

  country_specific_tlx_import_sheet_headers = [""] + country_specific_tlx_import_sheet_headers

  def create_input_and_selectbox(header, value, index, key, highlight=False):
    col1, col2 = st.columns([3, 3])
    with col1:
      user_header_input = st.text_input(f"User Header for '{header}':", header, disabled=True, key=f"user_defined_header_{key}")
    with col2:
      if highlight:   # For suggested mappings
        corrected = st.selectbox(f"Predefined Header for '{header}':", country_specific_tlx_import_sheet_headers, index=index, key=key, format_func=lambda x: f'🔴 {x}' if x == value['column'] else x)
        st.text(f"{value['explanation']}")
      else:
        corrected = st.selectbox(f"Predefined Header for '{header}':", country_specific_tlx_import_sheet_headers, index=index, key=key)
    return user_header_input, corrected

  key = 0
  for user_header, initial_map in initial_mappings_json.items():
    if user_header.lower() in ["suggestion", "suggestions"] and isinstance(initial_map, dict):
      for suggestion_header, suggestion_value in initial_map.items():
        index = country_specific_tlx_import_sheet_headers.index(suggestion_value['column']) if suggestion_value['column'] in country_specific_tlx_import_sheet_headers else 0
        user_header_input, corrected = create_input_and_selectbox(suggestion_header, suggestion_value, index, key, highlight=True)
        st.session_state.corrected_mappings[user_header_input] = corrected
        key += 1
    else:
      index = country_specific_tlx_import_sheet_headers.index(initial_map) if initial_map in country_specific_tlx_import_sheet_headers else 0
      user_header_input, corrected = create_input_and_selectbox(user_header, initial_map, index, key)
      st.session_state.corrected_mappings[user_header_input] = corrected
      key += 1

  return st.session_state.corrected_mappings

# This method displays the final mappings done by the LLM and corrected by the user on the UI
def display_mapped_data(llm_model, data, corrected_mappings, headers):
  fixed_value_columns = get_column_dropdown_values().keys()
  # Initialize an empty DataFrame with the specified headers
  mapped_data = pd.DataFrame(columns=headers)

  # Loop through mappings and populate the mapped_data DataFrame
  for source_col, target_col in corrected_mappings.items():
    # Only map if the source column exists in data and target column is in headers
    if source_col in data.columns and target_col in headers:
      if target_col.lower() in fixed_value_columns:
        output = generate_column_dropdown_value_mappings(llm_model, target_col.lower(), data[source_col].unique())
        data_mappings = sanitise_output(output)
        # Replace the values in the user's sheet with what it was mapped to
        mapped_data[target_col] = data[source_col].apply(lambda x: data_mappings.get(x, x) if data_mappings.get(x, x) else x)
      else:
        mapped_data[target_col] = data[source_col]
  # Ensure all required headers are present, fill missing with empty strings
  for header in headers:
    if header not in mapped_data.columns:
      mapped_data[header] = ''
  
  # Display the mapped data in a DataFrame
  st.write("Mapped Data:")
  st.dataframe(mapped_data)

def sanitise_output(output):
  # Regex pattern to match JSON object
  pattern = re.compile(r'({.*?})', re.DOTALL)
  match = pattern.search(output)
  
  if match:
    # Extract the JSON object string
    json_str = match.group(1)
    # Convert the JSON string to a Python dictionary
    try:
      json_obj = json.loads(json_str)
      return json_obj
    except json.JSONDecodeError as e:
      return None
  else:
    return None
