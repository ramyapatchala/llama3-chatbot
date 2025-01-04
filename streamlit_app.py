import streamlit as st
import os
import requests

# App title
st.set_page_config(page_title="Simple Chatbot")

# Initialize chatbot messages
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I assist you today?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Function to generate responses
def generate_response(prompt_input):
    # Simple response generation (can be replaced with an API call to an LLM)
    return f"You said: {prompt_input}"

# User-provided prompt
if prompt := st.chat_input(placeholder="Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            response = generate_response(prompt)
            st.write(response)
    
    # Add response to message history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Button to clear chat history
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I assist you today?"}]

st.sidebar.button('Clear Chat History', on_click=clear_chat_history)
