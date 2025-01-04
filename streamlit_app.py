import streamlit as st
from langchain_groq import ChatGroq

# Initialize the LLM
@st.cache_resource
def init_llm():
    return ChatGroq(model_name="llama3-70b-8192", temperature=0.2)

# App title
st.set_page_config(page_title="Simple Chatbot")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How may I assist you today?"}]
    st.session_state["llm"] = init_llm()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Function to generate response
def generate_response(prompt):
    llm = st.session_state["llm"]
    # Simple string input for the LLM
    response = llm(prompt)
    return response

# Handle user input
if prompt := st.chat_input(placeholder="Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Generate a response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response(prompt)
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
