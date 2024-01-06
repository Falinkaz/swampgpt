import math# Get a list of all CSV files in the current directory
import pandas as pd
import os
import numpy as np

# Get a list of all CSV files in the current directory
csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]

# Initialize an empty dataframe
df = pd.DataFrame()

# Loop through the CSV files and append each one to the dataframe
for csv_file in csv_files:
    df = df._append(pd.read_csv(csv_file), ignore_index=True)

# Drop duplicates
df.drop_duplicates(inplace=True)

# Save the merged data to a new CSV file
df.to_csv('merged.csv', index=False)

# Read the merged CSV file
df = pd.read_csv('merged.csv')

# Split the dataframe into 9 chunks and save each one to a new CSV file
for i, chunk in enumerate(np.array_split(df, 9)):
    chunk.to_csv(f'split_{i}.csv', index=False, encoding='utf-8-sig')