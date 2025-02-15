# preprocess_data.py

import pandas as pd
import numpy as np
import argparse

# Mapping for the simplified embassy code to descriptive labels
EMBASSY_CODE_MAPPING = {
    6: "Ambassador/Nuncio/Secretary of People’s Bureau",
    5: "Minister/Envoy",
    4: "Charge d’affaires",
    3: "Interest Desk",
    2: "Interests Served by",
    1: "Unknown"
}

def load_data(file_path):
    """
    Load the Excel (.xlsx) file into a pandas DataFrame.
    """
    try:
        df = pd.read_excel(file_path)
        print(f"Data loaded from {file_path}")
        return df
    except Exception as e:
        print(f"Error loading file: {e}")
        raise e

def clean_data(df):
    """
    Clean and standardize the raw DataFrame.
    
    Steps include:
      - Renaming columns to standard names.
      - Converting data types (e.g., ensuring 'year' is an integer).
      - Stripping extra whitespace from country names.
      - Filling or correcting missing values (e.g., for location).
    """
    # Rename columns based on the codebook's Variables section
    df = df.rename(columns={
        'Destination': 'host_country',
        'Sending Country': 'guest_country',
        'Year': 'year',
        'Location': 'location',
        'Embassy': 'embassy_code',
        'Focus': 'focus_code',
        'LOR': 'level_of_representation'
    })

    # Convert year to integer (if not already)
    df['year'] = df['year'].astype(int)

    # Standardize country names (remove extra spaces)
    df['host_country'] = df['host_country'].str.strip()
    df['guest_country'] = df['guest_country'].str.strip()

    # Fill missing values in location with a placeholder (if necessary)
    df['location'] = df['location'].fillna("Unknown")

    return df

def compute_level_of_representation(row):
    """
    Recalculate the level of representation based on the embassy code and focus code.
    
    According to the codebook:
      - For singular focus (Focus Code 1):
          * Embassy Code 6 -> Level = 1.0
          * Embassy Code 5 or 4 -> Level = 0.75
          * Embassy Code 3 -> Level = 0.125
          * Embassy Code 2 -> Level = 0.1
          * Embassy Code 1 -> Level = 0.75
      - For multiple focus (Focus Code 2):
          * Embassy Code 6 -> Level = 0.5
          * Embassy Code 5 or 4 -> Level = 0.375
          * Embassy Code 3 -> Level = 0.125
          * Embassy Code 2 -> Level = 0.1
          * Embassy Code 1 -> Level = 0.375
      - For Focus Code 3 (Expulsion, Recall, Withdrawn), assign Level = 0.0.
    
    Adjust these mappings as needed based on your interpretation of the codebook.
    """
    embassy_code = row['embassy_code']
    focus_code = row['focus_code']

    if focus_code == 3:
        return 0.0  # Expelled, recalled, or withdrawn
    elif focus_code == 1:  # Singular focus
        if embassy_code == 6:
            return 1.0
        elif embassy_code in [5, 4]:
            return 0.75
        elif embassy_code == 3:
            return 0.125
        elif embassy_code == 2:
            return 0.1
        elif embassy_code == 1:
            return 0.75
    elif focus_code == 2:  # Multiple focus
        if embassy_code == 6:
            return 0.5
        elif embassy_code in [5, 4]:
            return 0.375
        elif embassy_code == 3:
            return 0.125
        elif embassy_code == 2:
            return 0.1
        elif embassy_code == 1:
            return 0.375
    return np.nan  # Fallback if unexpected values are encountered

def transform_data(df):
    """
    Transform the data by computing derived variables and standardizing values.
    
    In this function, we:
      - Compute a new 'computed_level_of_representation' variable.
      - Map embassy codes to descriptive labels.
      - Optionally, drop or compare the original level of representation.
    """
    # Compute the level of representation based on our function
    df['computed_level_of_representation'] = df.apply(compute_level_of_representation, axis=1)
    
    # For this example, we'll drop the original column and use the computed one
    df = df.drop(columns=['level_of_representation'])
    df = df.rename(columns={'computed_level_of_representation': 'level_of_representation'})

    # Map the embassy_code to a more descriptive string (optional)
    df['embassy_description'] = df['embassy_code'].map(EMBASSY_CODE_MAPPING)

    return df

def save_data(df, output_path):
    """
    Save the preprocessed DataFrame to a CSV file.
    """
    df.to_csv(output_path, index=False)
    print(f"Cleaned data saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Preprocess the Diplomatic Representation dataset from an Excel file."
    )
    parser.add_argument("input_file", type=str, help="Path to the input Excel file (.xlsx)")
    parser.add_argument("output_file", type=str, help="Path to save the cleaned CSV file")
    args = parser.parse_args()

    # Step 1: Load the raw data
    data = load_data(args.input_file)
    print(data.columns)

    # Step 2: Clean and standardize the data
    data = clean_data(data)

    # Step 3: Transform data (compute derived variables)
    data = transform_data(data)

    # Step 4: Save the cleaned and transformed data
    save_data(data, args.output_file)
