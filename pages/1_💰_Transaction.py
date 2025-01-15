
import pandas as pd
import numpy as np
import datetime
from datetime import date, timedelta
import streamlit as st 
import xlsxwriter
import io

st.set_page_config(page_title="Transactions", page_icon="💰")

st.title("Transacion Breakdown")

filename = st.text_input("Filename", key='filename')
firstname = st.text_input("Enter Name", key='firstname1')
highticket = st.number_input("Enter High Ticket Integer Only")
uploaded_file = st.file_uploader("Please upload a CSV File", type=['csv'])

if uploaded_file is not None:

    highticketval = int(highticket)
    dfpreclean = pd.read_csv(uploaded_file)

    buffer = io.ByterIO()

    dfpreclean.drop(['Transaction_ID', 'Auth_code'], axis=1, inplace=True)
    dfpreclean2 = dfpreclean[dfpreclean['Success'] == 1]
    dfpreclean2['Transaction_Notes'].fillna("N/A", inplace=True)
    dfpreclean2['Day'] = pd.to_datetime(dfpreclean2['Day'])
    df = dfpreclean2.loc[:, [ 'Total', 'Transaction_Type', 'Type', 'Country','Source','Day','Customer_Name', 'Transaction_Notes',  ],]

    totalsum = np.sum(df['Total'])
    total_transactions = df['Type'].count()

    mean_transactions = np.mean(df['Total'])
    median_transactions = np.median(df['Total'])
    max_transactions = np.max(df['Total'])
   
    chargeonlytransactions = df[df['Type'] == 'Charge']
    refundonlytransactions = df[df['Type'] == 'Refund']
    chargebackonlytransactions = df[df['Type'] == 'Chargeback']

    days90 = pd.to_datetime(date.today() - timedelta(days=90))
    days180 = pd.to_datetime(date.today() - timedelta(days=180))

    chargetotal = np.sum(chargeonlytransactions['Total'])
    charge90days = np.sum(chargeonlytransactions[chargeonlytransactions['Day'] > days90]['Total'])
    charge180days = np.sum(chargeonlytransactions[chargeonlytransactions['Day'] > days180]['Total'])


    chargebacktotal = np.sum(chargebackonlytransactions['Total'])
    chargeback90days = np.sum(chargebackonlytransactions[chargebackonlytransactions['Day'] > days90]['Total'])
    chargeback180days = np.sum(chargebackonlytransactions[chargebackonlytransactions['Day'] > days180]['Total'])


    refundtotal = np.sum(refundonlytransactions['Total'])
    refund90days = np.sum(refundonlytransactions[refundonlytransactions['Day'] > days90]['Total'])
    refund180days = np.sum(refundonlytransactions[refundonlytransactions['Day'] > days180]['Total'])


    refundratelifetime = (refundtotal/chargetotal)
    refundrate90days = (refund90days/charge90days)
    refundrate180days = (refund180days/charge180days)


    chargebackratelifetime = (chargebacktotal/chargetotal)
    chargebackrate90days = (chargeback90days/charge90days)
    chargebackrate180days = (chargeback180days/charge180days)


    pivottablenames = pd.pivot_table(df, index=['Customer_Name'], aggfunc={'Total': np.sum, 'Customer_Name':'size'})
    pivottablenames = pivottablenames.rename(columns={ 'Customer_Name':'Count_of_total', 'Total':'sum_of_total'})
    pivottablenames = pivottablenames.loc[:, ['sum_of_total', 'Count_of_total']]


    avg_transactions_count_per_customer = np.mean(pivottablenames['Count_of_total'])
    avg_transactions_sum_per_customer = np.mean(pivottablenames['sum_of_total'])


    pivottbletransactiontype = pd.pivot_table(df, index=['Transaction_Type'], aggfunc={'Total': np.sum, 'Transaction_Type':'size'})
    pivottbletransactiontype['totalpercent'] = (pivottbletransactiontype['Total']/totalsum).map("{:,.2%}".format)

    pivottbletransactioncountry = pd.pivot_table(df, index=['Country'], aggfunc={'Total': np.sum, 'Country':'size'}) # Changed aggfunc to include 'Total': np.sum
    pivottbletransactioncountry['totalpercent'] = (pivottbletransactioncountry['Total']/totalsum).map("{:,.2%}".format)

    namefinal = df[df['Customer_Name'].str.contains(firstname, case=False)]

    payment_note = df[df['Transaction_Notes'].isna()==False]

    flagged_words = 'raffle|razz|lottery'
    payment_note_final = df[df['Transaction_Notes'].str.contains(flagged_words, case=False)]

    highticket = df[df['Total'] >= highticketval].copy()
    highticket = highticket.sort_values(by='Total', ascending=False)

    dup = df.copy()

    dup['Customer_Name_next'] = dup['Customer_Name'].shift(1)
    dup['Customer_Name_prev'] = dup['Customer_Name'].shift(- 1)
    dup['created_at_day'] = dup['Day']
    dup['created_at_dayprev'] = dup['Day'].shift(- 1)
    dup['created_at_daynext'] = dup['Day'].shift(1)
    dup3 = dup.query('created_at_day == created_at_dayprev  | created_at_day == created_at_daynext & (Customer_Name == Customer_Name_next | Customer_Name == Customer_Name_prev) ' )



    dfcalc = pd.DataFrame({'totalsum':[totalsum],
                        'mean_transactions':[mean_transactions],
                        'median_transactions':[median_transactions],
                        'max_transactions':[max_transactions],
                        'total_transactions':[total_transactions],
                        'chargetotal':[chargetotal],
                        'charge90days':[charge90days],
                        'charge180days':[charge180days],
                        'refundtotal':[refundtotal],
                        'refund90days':[refund90days],
                        'refund180days':[refund180days],
                        'chargebacktotal':[chargebacktotal],
                        'chargeback90days':[chargeback90days],
                        'chargeback180days':[chargeback180days],
                        'refundratelifetime':[refundratelifetime],
                        'refundrate90days':[refundrate90days],
                        'refundrate180days':[refundrate180days],
                        'chargebackratelifetime':[chargebackratelifetime],
                        'chargebackrate90days':[chargebackrate90days],
                        'chargebackrate180days':[chargebackrate180days],
                        'avg_transactions_count_per_customer':[avg_transactions_count_per_customer],
                        'avg_transactions_sum_per_customer':[avg_transactions_sum_per_customer],
                        '90 Days':[days90],
                        '180 Days':[days180],

                        })

    format_mapping = {'totalsum':'${:,.2f}',
                    'mean_transactions':'${:,.2f}',
                    'median_transactions':'${:,.2f}',
                    'max_transactions':'${:,.2f}',
                    'total_transactions':'${:,.2f}',
                    'chargetotal':'${:,.2f}',
                    'charge90days':'${:,.2f}',
                    'charge180days':'${:,.2f}',
                    'refundtotal':'${:,.2f}',
                    'refund90days':'${:,.2f}',
                    'refund180days':'${:,.2f}',
                    'refundratelifetime':'{:,.2%}',
                    'refundrate90days':'{:,.2%}',
                    'refundrate180days':'{:,.2%}',
                    'chargebacktotal':'${:,.2f}',
                    'chargeback90days':'${:,.2f}',
                    'chargeback180days':'${:,.2f}',
                    'chargebackratelifetime':'{:,.2%}',
                    'chargebackrate90days':'{:,.2%}',
                    'chargebackrate180days':'{:,.2%}',
                    'total_unique_customers':'{:,.0f}',
                    'avg_transactions_count_per_customer':'{:,.2f}',
                    'avg_transactions_sum_per_customer':'${:,.2f}',}

    for key, value in format_mapping.items():
          dfcalc[key] = dfcalc[key].apply(value.format)
    
    with pd.ExcelWriter(buffer, engine='xlswriter') as writer:
         df.to_excel(writer, sheet_name='Clean_Data')
         pivottablenames.to_excel(writer, sheet_name='Names')
         pivottbletransactiontype.to_excel(writer, sheet_name='Transaction_Type')
         pivottbletransactioncountry.to_excel(writer, sheet_name='Countries')
         payment_note_final.to_excel(writer, sheet_name='Payment_Notes')
         highticket.to_excel(writer, sheet_name='High_Ticket')
         namefinal.to_excel(writer, sheet_name='Name_checker')
         dup3.to_excel(writer, sheet_name='Double_Transactions')
         
         writer.close()

    st.download_button(
          label='Download Excel File',
          data=buffer,
          file_name= f"{st.session_state.file_name}.xlsx",
          mime="application/vnd.ms-excel"    
     )  
    
else:
     st.warning("You need to upload a csv")

