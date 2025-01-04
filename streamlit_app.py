import streamlit as st
import os
import requests
from langchain_groq import ChatGroq

# Initialize the LLM
@st.cache_resource  # Singleton, prevent multiple initializations
def init_llm():
    return ChatGroq(model_name="llama3-70b-8192", temperature=0.2)

# App title
st.set_page_config(page_title="Simple Chatbot")
st.title("Llama3 Chatbot")

# Initialize chatbot
if "messages" not in st.session_state:
    with st.spinner("Initializing chatbot, please wait..."):
        st.session_state.llm = init_llm()
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How can I assist you today?"}
        ]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! How can I assist you today?"}
    ]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Generate response
def generate_response(prompt):
    llm = st.session_state.llm
    response = llm(prompt)
    return response

# User-provided prompt
if prompt := st.chat_input(placeholder="Type your question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Generate a new response
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            response = generate_response(prompt)
            st.write(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
