import re 

def normalise_column_name(column):
  if column is None:
    column = "" 
  column = column.lower().replace(' ', '_')
  return re.sub(r'[^a-z0-9_]', '', column)