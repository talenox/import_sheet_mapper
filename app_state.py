from enum import Enum

class AppState(Enum):
  display_file_uploader = 0
  display_country_selector = 1
  display_column_header_mapping = 2
  display_column_value_mapping = 3
  display_column_default_value_selector = 4
  display_download_import_sheet_button = 5
