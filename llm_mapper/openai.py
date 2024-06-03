import os
class OpenAiMapper:
  def __init__(self, client):
    self.client = client

  # This method creates a prompt to summarise the column headers of a csv file
  def create_summary_prompt(self, headers):
    summary_prompt = "The CSV file contains the following columns:\n"
    summary_prompt += ", ".join(headers) + "\n\n"
    summary_prompt += "Please provide a summary or description of these columns."
    return summary_prompt
  
  # This method creates a prompt to summarise the column headers of a csv file
  def create_mapping_prompt(self, raw_data_headers, tlx_import_sheet_headers, prompt_file='base_prompt.txt'):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    directory_path = os.path.join(script_dir, f'../sample_prompts/{prompt_file}')
    # Open the file and read its content
    with open(directory_path, 'r') as file:
      prompt_text = file.read()
    
    prompt_text += f"""
      Here are the columns for you to map:

      User-provided column headers: {raw_data_headers}
      Fixed column headers: {tlx_import_sheet_headers}
    """
    return prompt_text

  # This method returns the output of the LLM
  def get_response(self, prompt):
    response = self.client.chat.completions.create(
      messages=[
        {
          "role": "user",
          "content": prompt,
        }
      ],
      model="gpt-3.5-turbo",
    )
    return response.choices[0].message.content