from data_generator.tlx_column_header_mapper import *
import re

# This method calls the LLM to create mappings based on the given column names and their data
def generate_column_header_mappings(llm_model, raw_data_headers, raw_sample_values, country_specific_tlx_import_sheet_headers, country_specific_sample_values):
  prompt = llm_model.create_column_header_mapping_prompt(raw_data_headers, raw_sample_values, country_specific_tlx_import_sheet_headers, country_specific_sample_values)
  response = llm_model.get_response(prompt)
  return response


# This method generates the mappings for the column data
def generate_fixed_value_column_mappings(llm_model, user_column_values, accepted_column_values):
  prompt = llm_model.create_column_value_mapping_prompt(user_column_values, accepted_column_values)
  response = llm_model.get_response(prompt)
  response = response.replace('\n', '')
  return sanitise_output(response)

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
