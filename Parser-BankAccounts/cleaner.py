import sys
import pandas as pd

if len(sys.argv) != 2:
    print("Usage: python cleaner.py <input_excel_file>")
    sys.exit(1)

# Get the input Excel file name from the command line argument
input_excel_file = sys.argv[1]

# Read the Excel file into a DataFrame
df = pd.read_excel(input_excel_file)

# Define the columns to check for duplicates
columns_to_check = ['photo_id', 'date', 'Amount']

# Remove rows with duplicate values in the specified columns
df_cleaned = df.drop_duplicates(subset=columns_to_check, keep='first')

# Replace exact occurrences of 0, 0.0, 0.00 in the "Amount" column with blank
df_cleaned.loc[df_cleaned['Amount'].isin(['0', '0.0', '0.00']), 'Amount'] = ''

# Replace entire cell content if it contains alphabetic or alphanumeric characters
df_cleaned.loc[:, 'Amount'] = df_cleaned['Amount'].apply(lambda x: '' if pd.notna(x) and any(c.isalpha() for c in str(x)) else x)

# Modify the filename to include "_mod"
output_excel_file = input_excel_file.replace('.xlsx', '_mod.xlsx')

# Save the DataFrame without duplicates to the modified Excel file
df_cleaned.to_excel(output_excel_file, index=False)

print(f"Modified Excel file saved as {output_excel_file}")

