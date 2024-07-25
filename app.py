import streamlit as st
from streamlit_chat import message
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import CTransformers
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from htmlTemplates import css, bot_template, user_template
from langchain.prompts import PromptTemplate

# load the pdf
pdf_path = 'docs/'
loader = DirectoryLoader(pdf_path, glob='*.pdf', loader_cls=PyPDFLoader)
documents = loader.load()

# split text into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=50)
text_chunks = text_splitter.split_documents(documents)

# create embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
                                   model_kwargs={'device': "cpu"})

# vectorstore
vector_store = FAISS.from_documents(text_chunks, embeddings)

# create llm
llm = CTransformers(model="llama-2-7b-chat.ggmlv3.q4_0.bin",
                    model_type="llama",
                    config={'max_new_tokens': 256, 'temperature': 0.05})


memory = ConversationBufferMemory(
    memory_key="chat_history", return_messages=True)

prompt_template = """
Use the given information context to give an appropriate answer for the user's question.
If you don't know the answer, just say that you know the answer, but don't make up an answer.
Context: 
{context}
- Name: Alex
- Occupation: Software Developer
- Interests: Technology, Virtual Reality, Productivity Tools
- Current Devices: iPhone, MacBook Pro

You're a sales chatbot designed to provide a compelling and engaging experience while promoting the Apple Vision Pro. Tailor your responses to highlight how the Apple Vision Pro can enhance Alex's technology experience, particularly focusing on its VR capabilities and productivity benefits.

Question: {question}
Only return the appropriate answer and nothing else.
Helpful answer:
"""

prompt = PromptTemplate(input_variables=["context", "question"],
                        template=prompt_template)
chain_type_kwargs = {"prompt": prompt}

chain = ConversationalRetrievalChain.from_llm(llm=llm, chain_type='stuff',
                                              retriever=vector_store.as_retriever(
                                                  search_kwargs={"k": 2}),
                                              memory=memory,
                                              combine_docs_chain_kwargs={
                                                  "prompt": prompt}
                                              )


st.title("Apple Vision Pro 🍎")
st.write(css, unsafe_allow_html=True)


# This function stops at a specified word in an input string and returns the string up to that word.
def stop_at_word(input_string, stop_word):
    words = input_string.split()
    result = []
    for word in words:
        if word == stop_word:
            break
        result.append(word)
    return ' '.join(result)


# This function handles the conversation between the user and the ChatBot.
# It queries the conversational retrieval chain and updates the session state with the conversation history.
def conversation_chat(query):
    result = chain(
        {"question": query, "chat_history": st.session_state['history']})
    st.session_state['history'].append((query, result["answer"]))
    st.session_state.chat_history = result['answer']
    return result['answer']


# This function initializes the session state for the Streamlit application.
# It initializes session variables such as chat history and past interactions.
def initialize_session_state():
    if 'history' not in st.session_state:
        st.session_state['history'] = []

    if 'generated' not in st.session_state:
        st.write(user_template.replace(
            "{{MSG}}", "Hello Bot👋"), unsafe_allow_html=True)
        st.write(bot_template.replace(
            "{{MSG}}", "Hello Human 😁"), unsafe_allow_html=True)

    st.session_state['generated'] = []
    st.session_state['past'] = []


# This function displays the chat history in the Streamlit application.
# It allows users to input questions and see the conversation history with the ChatBot.
def display_chat_history():
    reply_container = st.container()
    container = st.container()

    with container:
        with st.form(key='my_form', clear_on_submit=True):
            user_input = st.text_input(
                "Question:", placeholder="Ask about Apple Vision Pro", key='input')
            submit_button = st.form_submit_button(label='Send')

        if submit_button and user_input:
            output = conversation_chat(user_input)

            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)

    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])):
            message = st.session_state["generated"][i]
            message = stop_at_word(message, 'Unhelpful')
            st.write(user_template.replace(
                "{{MSG}}", st.session_state["past"][i]), unsafe_allow_html=True)
            st.write(bot_template.replace(
                "{{MSG}}", message), unsafe_allow_html=True)


# Initialize session state
initialize_session_state()
# Display chat history
display_chat_history()
