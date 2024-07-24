import os

class PromptUtils:
    @staticmethod
    def create_summary_prompt(headers):
        summary_prompt = "The CSV file contains the following columns:\n"
        summary_prompt += ", ".join(headers) + "\n\n"
        summary_prompt += "Please provide a summary or description of these columns."
        return summary_prompt

    @staticmethod
    def create_column_header_mapping_prompt(raw_data_headers, raw_sample_values, tlx_import_sheet_headers, country_specific_sample_values, prompt_file='base_prompt.txt'):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        directory_path = os.path.join(script_dir, f'../data/sample_prompts/{prompt_file}')
        # Open the file and read its content
        with open(directory_path, 'r') as file:
            prompt_text = file.read()

        prompt_text += f"""
        Here are the columns for you to map:

        User-provided column headers: {raw_data_headers}
        Fixed column headers: {tlx_import_sheet_headers}
        Sample values of user-provided header columns: {raw_sample_values}
        Sample values of selected fixed header columns: {country_specific_sample_values}
        """
        return prompt_text

    @staticmethod
    def create_column_value_mapping_prompt(user_input_column_values, tlx_column_accepted_values, prompt_file='column_dropdown_value_mapping_prompt.txt'):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        directory_path = os.path.join(script_dir, f'../data/sample_prompts/{prompt_file}')
        # Open the file and read its content
        with open(directory_path, 'r') as file:
            prompt_text = file.read()

        prompt_text += f"""
        Here are the columns for you to map:

        User input values: {user_input_column_values}
        Accepted values: {tlx_column_accepted_values}
        """
        return prompt_text
