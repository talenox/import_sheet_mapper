from data_generator.tlx_column_header_mapper import *

# This method calls the LLM to create mappings based on the given column names and their data
def generate_column_header_mappings(llm_model, raw_data_headers, raw_sample_values, country_specific_tlx_import_sheet_headers, country_specific_sample_values):
  prompt = llm_model.create_column_header_mapping_prompt(raw_data_headers, raw_sample_values, country_specific_tlx_import_sheet_headers, country_specific_sample_values)
  response = llm_model.get_response(prompt)
  return response


# This method generates the mappings for the column data
def generate_column_dropdown_value_mappings(llm_model, column_name, user_column_values):
  fixed_column_dropdown_values_json = get_column_dropdown_values()
  accepted_column_values = fixed_column_dropdown_values_json[column_name]
  prompt = llm_model.create_column_value_mapping_prompt(user_column_values, accepted_column_values)
  response = llm_model.get_response(prompt)
  return response