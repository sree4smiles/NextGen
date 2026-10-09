import streamlit as st
st.title("MY Demo Project")
name=st.text_input("Enter your Name:")
passw=st.text_input("Enter your Password:",type='password')
if st.button("Sign-In"):
    st.write("Welcome Mr./Ms", name)