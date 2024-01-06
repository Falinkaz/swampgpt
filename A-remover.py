import pandas as pd
import os

# Get a list of all CSV files in the current directory
csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]

# Loop through the CSV files and apply the operation to each one
for csv_file in csv_files:
    df = pd.read_csv(csv_file, encoding='utf-8')
    df = df[~df['name'].str.startswith('A-')]
    df.to_csv(csv_file, index=False, encoding='utf-8')