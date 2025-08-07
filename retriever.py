from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.prompts import PromptTemplate
from loader import load_pdfs_from_folder
import os
import streamlit as st

openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key
def build_qa_chain():
    embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key

    if os.path.exists("faiss_index") and os.path.exists("faiss_index/index.faiss"):
        vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    else:
        docs = load_pdfs_from_folder("data")
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)
        split_docs = splitter.split_documents(docs)
        vector_store = FAISS.from_documents(split_docs, embeddings)
        vector_store.save_local("faiss_index")

    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    chat = ChatOpenAI(model_name="gpt-4", temperature=0, openai_api_key=st.secrets["openai_api_key"])

    rewrite_prompt = PromptTemplate(
        input_variables=["question"],
        template="Rewrite the user question to be more specific and clear for yoga-related knowledge base: {question}"
    )
    query_rewrite_chain = LLMChain(llm=chat, prompt=rewrite_prompt)

    return retriever, query_rewrite_chain