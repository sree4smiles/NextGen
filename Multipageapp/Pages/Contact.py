import streamlit as st

st.title("Contact Page")   
st.write("This is the Contact Page of the Multipage App.")
st.text_input("Enter Name")
st.text_input("Enter Email")  
st.text_area("Enter Message")
st.button("Submit")