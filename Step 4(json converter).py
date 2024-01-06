import pandas as pd
import os
import numpy as np

# Get a list of all CSV files in the current directory
csv_files = [f for f in os.listdir('.') if f.startswith('split_') and f.endswith('.csv')]

# Loop through the CSV files and save each one as a JSON file with a different name
for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    df.to_json(csv_file.replace('split_', 'new_split_').replace('.csv', '.json'), orient='records')