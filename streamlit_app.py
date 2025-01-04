import streamlit as st
import os
import requests

# initialize new sqlite3
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# Langchain and HuggingFace
from langchain.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA

# Load embeddings, model, and vector store
@st.cache_resource # Singleton, prevent multiple initializations
def init_chain():
    model_kwargs = {'trust_remote_code': True}
    embedding = HuggingFaceEmbeddings(model_name='nomic-ai/nomic-embed-text-v1.5', model_kwargs=model_kwargs)
    llm = ChatGroq(model_name="llama3-70b-8192", temperature=0.2)
    vectordb = Chroma(persist_directory='db_v4.1', embedding_function=embedding)

    # Create chain
    chain = RetrievalQA.from_chain_type(llm=llm,
                                  chain_type="stuff",
                                  retriever=vectordb.as_retriever(k=5),
                                  return_source_documents=True)

    return chain

# App title
st.set_page_config(page_title="Chatbot")

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    with st.spinner("Initializing, please wait..."):
        st.session_state.chain = init_chain()
        st.session_state.messages = [{"role": "assistant", "content": "How may I help you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I help you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating response
def generate_response(prompt_input):
    # Initialize result
    result = ''
    # Invoke chain
    res = st.session_state.chain.invoke(prompt_input)
    # Process response
    if res['result'].startswith('According to the provided context, '):
        res['result'] = res['result'][35:]
        res['result'] = res['result'][0].upper() + res['result'][1:]
    elif res['result'].startswith('Based on the provided context, '):
        res['result'] = res['result'][31:]
        res['result'] = res['result'][0].upper() + res['result'][1:]    
    result += res['result']
    # Process sources
    result += '\n\nSources: '
    sources = [] 
    for source in res["source_documents"]:
        sources.append(source.metadata['source'][4:-4]) # Remove AXX- and .txt
    source_list = ", ".join(sources) # store all sources
    sources = set(sources) # Remove duplicate sources (multiple chunks)
    result += source_list

    return result, res['result'], source_list

# User-provided prompt
if prompt := st.chat_input(placeholder="Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    prompt = st.session_state.messages[-1]["content"]
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            placeholder = st.empty()
            response, answer, source_list = generate_response(prompt)
            placeholder.markdown(response)
    message = {"role": "assistant", "content": response}

    # Post question and answer to Google Sheets via Apps Script
    url = os.environ['SCRIPT_URL']
    requests.post(url, data = {"question": prompt, "answer": answer, "top_source": source_list})
    st.session_state.messages.append(message)
