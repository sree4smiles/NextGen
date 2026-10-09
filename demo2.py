import streamlit as st
import pandas as pd

fileloc = st.file_uploader("Upload a CSV file")
#check file is csv or not 
if fileloc is not None and fileloc.name.endswith('.csv'):
    df = pd.read_csv(fileloc)
    print(df.columns)
    #Groupby city column and find average of subject column
    df1 = df.groupby('City')['Subject3_Marks'].mean().reset_index()
    st.bar_chart(df1, x='City', y='Subject3_Marks')
    st.dataframe(df1)
else:
    st.write("Please upload csv file only")
 