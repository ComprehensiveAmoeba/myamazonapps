import streamlit as st
import pandas as pd
import random
import string
from datetime import datetime
import openpyxl
from io import BytesIO

def generate_random_id(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def validate_data(data):
    errors = []
    for i, row in data.iterrows():
        if not (isinstance(row['ASIN'], str) and len(row['ASIN']) == 10 and row['ASIN'].startswith('B0')):
            errors.append(f"Invalid ASIN in row {i+1}")
        # Additional validations...

    return errors

def generate_campaign_file(data, cross_negation):
    output_rows = []
    for _, row in data.iterrows():
        campaign_id = generate_random_id()
        ad_group_id = generate_random_id()
        ad_id = generate_random_id()
        keyword_id = generate_random_id()
        negative_keyword_id = generate_random_id() if cross_negation and row['Match Type'].lower() in ['broad', 'phrase'] else ""

        campaign_prefix = {'exact': 'OW_', 'broad': 'BR_', 'phrase': 'PH_'}
        campaign_name = campaign_prefix[row['Match Type'].lower()] + row['ASIN']
        if pd.notna(row['Naming convention tag']):
            campaign_name += '_' + row['Naming convention tag']
        campaign_name += '_' + row['Keyword Text']

        start_date = datetime.now().strftime("%Y%m%d")

        # Campaign row
        output_rows.append({
            'Product': 'Sponsored Products',
            'Entity': 'Campaign',
            'Operation': 'create',
            'Campaign ID': campaign_id,
            'Campaign Name': campaign_name,
            'Start Date': start_date,
            'Targeting Type': 'manual',
            'State': 'enabled',
            'Daily Budget': row['Daily Budget'],
            'Bidding Strategy': row['Bidding Strategy'] if pd.notna(row['Bidding Strategy']) else 'Dynamic bids - down only'
        })

        # Ad Group row
        output_rows.append({
            'Product': 'Sponsored Products',
            'Entity': 'Ad Group',
            'Operation': 'create',
            'Campaign ID': campaign_id,
            'Ad Group ID': ad_group_id,
            'Ad Group Name': 'AG_' + row['ASIN'],
            'State': 'enabled',
            'Ad Group Default Bid': row['Bid']
        })

        # Product Ad row
        output_rows.append({
            'Product': 'Sponsored Products',
            'Entity': 'Product Ad',
            'Operation': 'create',
            'Campaign ID': campaign_id,
            'Ad Group ID': ad_group_id,
            'Ad ID': ad_id,
            'SKU': row['SKU'],
            'State': 'enabled'
        })

        # Keyword row
        output_rows.append({
            'Product': 'Sponsored Products',
            'Entity': 'Keyword',
            'Operation': 'create',
            'Campaign ID': campaign_id,
            'Ad Group ID': ad_group_id,
            'Keyword ID': keyword_id,
            'Bid': row['Bid'],
            'Keyword Text': row['Keyword Text'],
            'Match Type': row['Match Type'],
            'State': 'enabled'
        })

        # Bidding Adjustment row
        if pd.notna(row['Placement']):
            output_rows.append({
                'Product': 'Sponsored Products',
                'Entity': 'Bidding Adjustment',
                'Operation': 'create',
                'Campaign ID': campaign_id,
                'Placement': row['Placement'],
                'Percentage': row['Percentage']
            })

        # Negative Keyword row
        if negative_keyword_id:
            output_rows.append({
                'Product': 'Sponsored Products',
                'Entity': 'Negative Keyword',
                'Operation': 'create',
                'Campaign ID': campaign_id,
                'Ad Group ID': ad_group_id,
                'Keyword ID': negative_keyword_id,
                'Keyword Text': row['Keyword Text'],
                'Match Type': 'Negative Exact',
                'State': 'enabled'
            })

    return pd.DataFrame(output_rows)

# Streamlit App Layout
st.title("Amazon Campaign Creation Tool")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)

    errors = validate_data(data)
    if errors:
        for error in errors:
            st.error(error)
        error_report = pd.DataFrame({'Errors': errors})
        st.download_button(label="Download Error Report", data=error_report.to_csv(index=False).encode('utf-8'), file_name="error_report.csv", mime="text/csv")
    else:
        cross_negation = st.selectbox("Broad and Phrase Campaign Cross Negation", ["Yes", "No"])
        if st.button("Generate Campaign File"):
            output_df = generate_campaign_file(data, cross_negation == "Yes")
            towrite = BytesIO()
            with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
                output_df.to_excel(writer, index=False)
            towrite.seek(0)
            st.download_button(label="Download Campaign File", data=towrite.read(), file_name="campaign.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
