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
        if not (str(row['ASIN']).startswith('B0') and len(str(row['ASIN'])) == 10):
            errors.append(f'Invalid ASIN at row {i+1}')
        if not isinstance(row['Daily Budget'], (int, float)) or not (2 <= row['Daily Budget'] <= 1000):
            errors.append(f'Invalid Daily Budget at row {i+1}')
        if any(len(word) > 21 for word in str(row['Keyword Text']).split()):
            errors.append(f'Invalid Keyword Text at row {i+1}')
        if str(row['Match Type']).lower() not in ['exact', 'broad', 'phrase']:
            errors.append(f'Invalid Match Type at row {i+1}')
        if not (0.02 <= row['Bid'] <= 15):
            errors.append(f'Invalid Bid at row {i+1}')
        if pd.notna(row['Portfolio ID']) and not isinstance(row['Portfolio ID'], (int, float)):
            errors.append(f'Invalid Portfolio ID at row {i+1}')
        if pd.notna(row['Percentage']) and not (0 <= row['Percentage'] <= 900):
            errors.append(f'Invalid Percentage at row {i+1}')
        if pd.notna(row['Naming convention tag']) and (len(str(row['Naming convention tag'])) > 10 or ' ' in str(row['Naming convention tag'])):
            errors.append(f'Invalid Naming Convention Tag at row {i+1}')
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
        if pd.notna(row['Naming convention tag']) and row['Naming convention tag']:
            campaign_name += '_' + row['Naming convention tag']
        campaign_name += '_' + row['Keyword Text']

        start_date = datetime.now().strftime("%Y%m%d")

        # Campaign row with Portfolio ID
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
            'Bidding Strategy': row['Bidding Strategy'] if pd.notna(row['Bidding Strategy']) and row['Bidding Strategy'] else 'Dynamic bids - down only',
            'Portfolio ID': row['Portfolio ID'] if pd.notna(row['Portfolio ID']) else ''
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
