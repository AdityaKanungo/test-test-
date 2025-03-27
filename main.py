import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import streamlit as st
from components.header import Header
from components.sidebar import Sidebar
from components.content_area import ContentArea
from components.chat_input import ChatInput


st.set_page_config(layout='wide')

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []

# Render UI
Header().render()
st.markdown("<div style='height:60px;'></div>", unsafe_allow_html=True)

cols = st.columns([1, 3])
with cols[0]:
    Sidebar().render(st.session_state.history)
with cols[1]:
    ContentArea().render('Welcome to the Policy Navigator — ask your policy question below:')
    user_input = ChatInput().render()
    if user_input:
        st.session_state.history.append(user_input)
        ContentArea().render(f"**You asked:** {user_input}")
