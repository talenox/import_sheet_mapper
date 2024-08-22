import json
import re
import time
import uuid
import streamlit as st
from data_processor.extractor import *
from data_generator.tlx_column_header_mapper import *
from helper_methods.mapper import *
from helper_methods.normalise_string import *

# This method displays the initial column mappings done by the LLM on the UI
def display_initial_value_mappings(initial_mappings_json, fixed_values, session_key):
  if session_key not in st.session_state:
    st.session_state[session_key] = {}
  fixed_values = [""] + fixed_values
  key = 0
  # Separate items into categories
  suggested_headers = {k: v for k, v in initial_mappings_json.items() if isinstance(v, dict) }
  confirmed_mapping = {}
  unmapped_headers = {}
  # We use this loop instead of list comprehension to split confirmed and unmapped to acocunt for unintended LLM behaviour that may map to columns that do not exist
  for user_value in initial_mappings_json.keys():
    suggested_value = initial_mappings_json.get(user_value)
    if isinstance(suggested_value, dict):
      continue
    else:
      if suggested_value in fixed_values:
        index = fixed_values.index(suggested_value)
      else:
        index = 0
      if index == 0:
        unmapped_headers[user_value] = suggested_value
      else:
        confirmed_mapping[user_value] = suggested_value
  
  if len(unmapped_headers) > 0:
    with st.expander("🔴 Unmapped Items", expanded=True):
      for user_header, unmapped_header in unmapped_headers.items():
        user_input, corrected = create_input_and_selectbox(fixed_values, user_header, unmapped_header, 0, key)
        st.session_state[session_key][user_input] = corrected
        key += 1

  if len(suggested_headers) > 0:
    with st.expander("🟠 Suggested Items", expanded=True):
      for _, suggested_mappings in suggested_headers.items():
        for user_header, suggestion_header in suggested_mappings.items():
          if suggestion_header['column'] in fixed_values:
            index = fixed_values.index(suggestion_header['column'])
          elif f"{suggestion_header['column']}*" in fixed_values:
            mapped_header = f"{suggestion_header['column']}*"
            index = fixed_values.index(suggestion_header['column'])
          else:
            index = 0
          user_input, corrected = create_input_and_selectbox(fixed_values, user_header, suggestion_header, index, key, suggestion=True)
          st.session_state[session_key][user_input] = corrected
          key += 1

  if len(confirmed_mapping) > 0:
    with st.expander("🟢 Confirmed Mappings", expanded=False):
      for user_header, mapped_header in confirmed_mapping.items():
        if mapped_header in fixed_values:
          index = fixed_values.index(mapped_header)
        elif f"{mapped_header}*" in fixed_values:
          mapped_header = f"{mapped_header}*"
          index = fixed_values.index(mapped_header)
        else:
          index = 0
        user_input, corrected = create_input_and_selectbox(fixed_values, user_header, mapped_header, index, key)
        st.session_state[session_key][user_input] = corrected
        key += 1

  return st.session_state[session_key]

# This method displays the initial value mappings done by the LLM on the UI
def display_initial_column_mappings(initial_mappings_json, session_key):
  humanised_fixed_values = [""] + list(st.session_state['column_header_name_normalised_mapping'].values())
  key = 0
  suggested_headers = {k: v for k, v in initial_mappings_json.items() if isinstance(v, dict) }
  confirmed_mapping = {}
  unmapped_headers = {}
  # We use this loop instead of list comprehension to split confirmed and unmapped to acocunt for unintended LLM behaviour that may map to columns that do not exist
  for user_header in initial_mappings_json.keys():
    suggested_header = initial_mappings_json.get(user_header)
    if isinstance(suggested_header, dict):
      continue
    else:
      normalised_column_name = normalise_column_name(suggested_header)
      humanised_column_name = st.session_state['column_header_name_normalised_mapping'].get(normalised_column_name)
      if normalised_column_name in st.session_state['column_header_name_normalised_mapping'].keys():
        index = humanised_fixed_values.index(humanised_column_name)
      else:
        index = 0
      if index == 0:
        unmapped_headers[user_header] = suggested_header
      else:
        confirmed_mapping[user_header] = suggested_header

  if len(unmapped_headers) > 0:
    with st.expander("🔴 Unmapped Items", expanded=True):
      for user_header, unmapped_header in unmapped_headers.items():
        user_input, corrected = create_input_and_selectbox(humanised_fixed_values, user_header, unmapped_header, 0, key)
        st.session_state[session_key][user_input] = corrected
        key += 1

  if len(suggested_headers) > 0:
    with st.expander("🟠 Suggested Items", expanded=True):
      for user_header in suggested_headers:
        suggested_column = suggested_headers[user_header]['column']
        explanation = suggested_headers[user_header]['explanation']
        normalised_column_name = normalise_column_name(suggested_column)
        humanised_column_name = st.session_state['column_header_name_normalised_mapping'].get(normalised_column_name)
        if normalised_column_name in st.session_state['column_header_name_normalised_mapping'].keys():
          index = humanised_fixed_values.index(humanised_column_name)
        else:
          index = 0
        user_input, corrected = create_input_and_selectbox(humanised_fixed_values, user_header, suggested_headers[user_header], index, key, suggestion=True, explanation=explanation)
        st.session_state[session_key][user_input] = corrected
        key += 1

  if len(confirmed_mapping) > 0:
    with st.expander("🟢 Confirmed Mappings", expanded=False):
      for user_header, mapped_header in confirmed_mapping.items():
        normalised_column_name = normalise_column_name(mapped_header)
        humanised_column_name = st.session_state['column_header_name_normalised_mapping'].get(normalised_column_name)
        if normalised_column_name in st.session_state['column_header_name_normalised_mapping'].keys():
          index = humanised_fixed_values.index(humanised_column_name)
        else:
          index = 0
        user_input, corrected = create_input_and_selectbox(humanised_fixed_values, user_header, humanised_column_name, index, key)
        st.session_state[session_key][user_input] = corrected
        key += 1

  return st.session_state[session_key]

# This method creates the boxes to display the value mappings
def create_input_and_selectbox(fixed_values, header, mapped_value, index, key, suggestion=False, explanation=""):
  col1, col2 = st.columns([3, 3])
  with col1:
    user_input = st.text_input("Label", header, disabled=True, key=f"col_1_{header}_{mapped_value}_{key}_{index}", label_visibility="hidden")
  with col2:
    corrected = st.selectbox("Label", fixed_values, index=index, key=f"col_2_{header}_{mapped_value}_{key}", label_visibility="hidden")
  if suggestion:
    st.text(f"{explanation}")
  
  return user_input, corrected

# This method displays the final mappings done by the LLM and corrected by the user on the UI
def display_final_mapped_data(data, corrected_column_mappings, headers, corrected_value_mappings, country):
  fixed_value_columns = corrected_value_mappings.keys()
  # Initialize an empty DataFrame with the specified headers from the sample sheet
  script_dir = os.path.dirname(os.path.abspath(__file__))
  template_path = os.path.join(script_dir, f'../data/tlx_import_sheet_samples/{country.lower()}.xlsx')

  headers = extract_headers_from_excel_file(template_path, 2, sheet_name=0)
  mapped_data = pd.DataFrame(columns=headers)

  # Loop through mappings and populate the mapped_data DataFrame
  for source_col, target_col in corrected_column_mappings.items():
    # Only map if the source column exists in data and target column is in headers
    if source_col in data.columns and target_col in headers:
      if target_col in fixed_value_columns:
        # Replace the values in the user's sheet with what it was mapped to
        mapped_data[target_col] = data[source_col].apply(lambda x: corrected_value_mappings[target_col].get(x, x) if corrected_value_mappings[target_col].get(x, x) else '')
      else:
        mapped_data[target_col] = data[source_col]
  # Ensure all required headers are present, fill missing with empty strings
  for header in headers:
    if header in st.session_state.unmapped_columns_default_value.keys():
      mapped_data[header] = st.session_state.unmapped_columns_default_value.get(header)
      continue
    if header not in mapped_data.columns:
      mapped_data[header] = ''
  
  # Display the mapped data in a DataFrame
  st.write("Mapped Data:")
  st.data_editor(mapped_data)
  return mapped_data

# This method displays the dropdowns for user to choose the default value for mandatory columns in the import sheet that have not been mapped previously
def display_default_value_mappings(filtered_json, session_key):
  if session_key not in st.session_state:
    st.session_state[session_key] = {}
  key = 0
  with st.expander("Column Defaults", expanded=True):
    for column_header, value_options in filtered_json.items():
      humanised_column_header = st.session_state['column_header_name_normalised_mapping'].get(column_header)
      user_input, corrected = create_input_and_selectbox(value_options, humanised_column_header, "", 0, f"{key}_column_default")
      st.session_state[session_key][user_input] = corrected
      key += 1

  return st.session_state[session_key]