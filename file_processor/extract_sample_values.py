import pandas as pd
import json

# Function to convert data types to be JSON serializable
def convert_type(value):
    if pd.isna(value):
        return None
    elif hasattr(value, 'item'):
        return value.item()
    elif isinstance(value, pd.Timestamp):
        return value.isoformat()
    else:
        return value



# Read the Excel file
excel_file = 'sample_data/profiles-employees-export-PricewaterhouseCoopers_LLP-20240523163330 (1).xlsx'  # Replace with your actual file path
df = pd.read_excel(excel_file, header=2)  # header=1 to read the second row as header (0-indexed)

# Get the headers and the first row of data (data starts at row 3, so index 0-based is 2)
headers = list(df.columns)
first_row = df.iloc[0]

# Create a dictionary for headers and their corresponding values
sample_data = {header: convert_type(first_row[header]) for header in headers if pd.notna(first_row[header])}

# Save the dictionary as a JSON file
with open('singapore_sample_data.json', 'w') as jsonfile:
    json.dump(sample_data, jsonfile, ensure_ascii=False, indent=4)

print("JSON file created successfully.")