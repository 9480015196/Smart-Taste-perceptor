from dotenv import load_dotenv
load_dotenv() #to load all env variables

import streamlit as st
import os


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

##function to load gemini pro model
model=genai.GenerativeModel("gemini-2.0-flash")
def get_gemini_response(question):
    response=model.generate_content(question)
    return response.text

    

##streamlit 
st.set_page_config(page_title="Q&A DEMO")

st.header("Smart Taste Perceptor")

input=st.text_input("Input:",key="input")

submit=st.button("Ask me anything")
#When submit is clicked

if submit:
    response=get_gemini_response(input)
    st.write(response)    