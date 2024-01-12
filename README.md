# Amazon Campaign Creation Tool

## Overview
The Amazon Campaign Creation Tool is a Streamlit app designed to automate the process of creating advertising campaigns for Amazon products. It streamlines the process of generating campaign files based on input data, ensuring a quick and efficient setup of Amazon Sponsored Product campaigns.

## Features
- **Input Data Validation**: Validates uploaded CSV data against specific criteria.
- **Campaign File Generation**: Generates a structured Excel file for campaign setup.
- **Error Reporting**: Identifies and reports any data inconsistencies.

## How to Use
1. **Prepare Your Data**: Use the provided [input template]([https://docs.google.com/spreadsheets/](https://docs.google.com/spreadsheets/d/19_F0eC94plDEhyUsabXqVtb1c7ymuJZwxJlRLsldcCE/edit#gid=0)]) to format your campaign data. Ensure all fields are filled out correctly.
2. **Launch the App**: Start the Streamlit app. You'll see an interface with an option to upload your CSV file.
3. **Upload CSV File**: Click on 'Choose a CSV file' and select your prepared CSV file.
4. **Data Validation**: Once uploaded, the app automatically validates the data. If there are any errors, they will be displayed, and you'll have the option to download an error report.
5. **Generate Campaign File**: If no errors are found, you can proceed to generate the campaign file. Choose your preference for 'Broad and Phrase Campaign Cross Negation' from the dropdown menu.
6. **Download Campaign File**: Click on 'Generate Campaign File'. The app will process the data and provide a button to download the generated Excel campaign file.

## Mandatory Input Fields
The following fields are mandatory for the campaign creation process:
1. **ASIN**: Must start with 'B0' and be 10 characters in length.
2. **Daily Budget**: A number between 2 and 1000.
3. **Keyword Text**: Each word should not exceed 21 characters.
4. **Match Type**: Must be 'exact', 'broad', or 'phrase'.
5. **Bid**: A value between 0.02 and 15.
6. **SKU**: Unique identifier for each product in your inventory.

## Optional Fields
- **Portfolio ID**
- **Percentage** (for bidding adjustments)
- **Naming Convention Tag**
- **Bidding Strategy** (defaults to 'Dynamic bids - down only' if not provided)
- **Placement** (used with 'Percentage' for bidding adjustments)

## Broad and Phrase Campaign Cross Negation
- **Yes**: Negative keywords are generated for broad and phrase campaigns to minimize overlap and internal competition.
- **No**: Campaigns are created without cross negation.

## Dependencies
- Streamlit
- Pandas
- Openpyxl
- Python's Random and String libraries
- Python's datetime module

## App Code Structure
- `generate_random_id`: Generates a random ID for various campaign elements.
- `validate_data`: Validates the uploaded data against specific criteria.
- `generate_campaign_file`: Generates the structured campaign data and returns it as a DataFrame.
- `Streamlit App Layout`: Defines the layout and interactive elements of the Streamlit app.

## Troubleshooting
- **Invalid Data Format**: Ensure your CSV file matches the format in the provided template.
- **Error During File Generation**: Check if all fields in the CSV are correctly filled. Refer to the error report for specific issues.

## Support
For additional help or to report issues, please contact [pasacle@gmail.com].

