import json
import re
import time
import streamlit as st
from data_processor.extractor import *
from data_generator.tlx_column_header_mapper import *
from helper_methods.mapper import *

# This method displays the initial mappings done by the LLM on the UI
def display_initial_mappings(initial_mappings_json, fixed_values, session_key):
  if session_key not in st.session_state:
    st.session_state[session_key] = {}
    
  fixed_values = [""] + fixed_values
  key = 0
  
  # Separate items into categories
  confirmed_mapping = {k: v for k, v in initial_mappings_json.items() if v is not None and not isinstance(v, dict)}
  suggested_headers = {k: v for k, v in initial_mappings_json.items() if isinstance(v, dict)}
  unmapped_headers = {k: v for k, v in initial_mappings_json.items() if v is None}
  
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
          index = fixed_values.index(suggestion_header['column']) if suggestion_header['column'] in fixed_values else 0
          user_input, corrected = create_input_and_selectbox(fixed_values, user_header, suggestion_header, index, key, suggestion=True)
          st.session_state[session_key][user_input] = corrected
          key += 1

  if len(confirmed_mapping) > 0:
    with st.expander("🟢 Confirmed Mappings", expanded=False):
      for user_header, mapped_header in confirmed_mapping.items():
        index = fixed_values.index(mapped_header) if mapped_header in fixed_values else 0
        user_input, corrected = create_input_and_selectbox(fixed_values, user_header, mapped_header, index, key)
        st.session_state[session_key][user_input] = corrected
        key += 1

  return st.session_state[session_key]

# This method creates the boxes to display the mappings
def create_input_and_selectbox(fixed_values, header, mapped_value, index, key, suggestion=False):
  col1, col2 = st.columns([3, 3])
  with col1:
    user_input = st.text_input("Label", header, disabled=True, key=f"col_1_{header}_{int(time.time())}", label_visibility="hidden")
  with col2:
    corrected = st.selectbox("Label", fixed_values, index=index, key=f"col_2_{key}_{int(time.time())}", label_visibility="hidden")
  if suggestion:
    st.text(f"{mapped_value['explanation']}")
  return user_input, corrected

# TODO: Joshua update this
# This method displays the final mappings done by the LLM and corrected by the user on the UI
def display_final_mapped_data(llm_model, data, corrected_mappings, headers):
  fixed_value_columns = get_tlx_column_dropdown_values().keys()
  # Initialize an empty DataFrame with the specified headers
  mapped_data = pd.DataFrame(columns=headers)

  # Loop through mappings and populate the mapped_data DataFrame
  for source_col, target_col in corrected_mappings.items():
    # Only map if the source column exists in data and target column is in headers
    if source_col in data.columns and target_col in headers:
      if target_col.lower() in fixed_value_columns:
        output = generate_fixed_value_column_mappings(llm_model, target_col.lower(), data[source_col].unique())
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