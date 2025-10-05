from dotenv import load_dotenv
from langchain_groq import ChatGroq
from src.utilities.logger import Logger
from src.services.service_handler import ServiceHandler
from src.utilities.constants import ConstantsFetcher
import os 
import streamlit as st


load_dotenv()


servicehandler = ServiceHandler()

st.title("Wikipedia Q&A Chatbot")
st.write("Ask questions about Wikipedia articles!")



# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Accept user input
if prompt := st.chat_input("What is up?"):

    # adds user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # displays user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # displays assistant response in chat message container
    with st.chat_message("assistant"):
        
        streamer = servicehandler.handle_userinput(prompt)
        response = st.write_stream(streamer)
        
    st.session_state.messages.append({"role": "assistant", "content": response})