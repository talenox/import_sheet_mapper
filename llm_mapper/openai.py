class OpenAiMapper:
  def __init__(self, client):
    self.client = client

  # This method creates a prompt to summarise the column headers of a csv file
  def create_summary_prompt(self, headers):
    summary_prompt = "The CSV file contains the following columns:\n"
    summary_prompt += ", ".join(headers) + "\n\n"
    summary_prompt += "Please provide a summary or description of these columns."
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