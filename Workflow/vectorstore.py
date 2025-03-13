import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

FAISS_DB_PATH = "Vectorstore/db_faiss"

# Function to split documents into chunks
def create_chunks(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
    return text_splitter.split_documents(documents)

# Function to get embedding model
def get_embedding_model():
    return GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# Function to store chunks in FAISS vector database
def store_in_vector_db(chunks):
    embeddings = get_embedding_model()
    faiss_db = FAISS.from_documents(chunks, embeddings)
    faiss_db.save_local(FAISS_DB_PATH)
    return faiss_db

# Function to load FAISS vector database
def load_vector_db():
    if not os.path.exists(FAISS_DB_PATH) or not os.listdir(FAISS_DB_PATH):
        return None
    embeddings = get_embedding_model()
    return FAISS.load_local(FAISS_DB_PATH, embeddings,allow_dangerous_deserialization=True)
