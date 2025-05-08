import streamlit as st
import os
import openai
import pandas as pd
from dotenv import load_dotenv

# Load OpenAI API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# App title
st.title("Prompt-driven Data Profiling (OpenAI Powered)")
uploaded_file = st.file_uploader("Upload a CSV file for analysis", type=['csv'])

# Prompt user
user_prompt = st.text_area("Enter your data profiling prompt", 
                           "Generate a data profile summary including column types, missing values, top categories, and descriptive statistics.")

# Function to call OpenAI
def generate_data_profile(prompt, data_sample):
    messages = [
        {"role": "system", "content": "You are a data analyst. Return a structured profiling report based on the dataset sample."},
        {"role": "user", "content": f"Dataset Sample:\n{data_sample}\n\n{prompt}"}
    ]
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.3,
        max_tokens=1200
    )
    
    return response.choices[0].message["content"]

# Process uploaded file
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("**Sample of Uploaded Data:**")
    st.dataframe(df.head())

    if st.button("Generate Profile"):
        with st.spinner("Generating data profile using OpenAI..."):
            data_sample = df.head(5).to_string()
            output = generate_data_profile(user_prompt, data_sample)
            st.markdown("### Data Profiling Report")
            st.markdown(output)