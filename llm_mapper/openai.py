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
  def create_mapping_prompt(self, raw_data_headers, tlx_import_sheet_headers):
    summary_prompt = "The input file contains the following columns:\n"
    summary_prompt += ", ".join(raw_data_headers) + "\n\n"
    summary_prompt += "Please provide a mapping of these columns to the following fixed columns:\n"
    summary_prompt += ", ".join(tlx_import_sheet_headers) + "\n\n"
    summary_prompt += "Note: Columns in the input file can be mapped to zero or more fixed columns and vice versa."
    return summary_prompt

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