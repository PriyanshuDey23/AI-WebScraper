import streamlit as st
import os
from langchain_community.document_loaders.firecrawl import FireCrawlLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain


# Inject custom CSS
hide_github_icon = """
    <style>
        [data-testid="stToolbar"] a {
            display: none !important;
        }
    </style>
"""
st.markdown(hide_github_icon, unsafe_allow_html=True)

# Streamlit UI Header
st.title("🌍 Web Scraper & QA Chatbot")
st.markdown("### Enter a website URL, scrape content, and ask questions based on it.")

# Retrieve API Keys from Streamlit Secrets
FIRE_CRAWL_API_KEY = st.secrets["FIRE_CRAWL_API_KEY"] if "FIRE_CRAWL_API_KEY" in st.secrets else None
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"] if "GOOGLE_API_KEY" in st.secrets else None

# LLM Model for answering queries
llm_model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=GOOGLE_API_KEY,temperature=0.2)


# Vectorstore Path
FAISS_DB_PATH = "./Vectorstore/db_faiss"

# Function to Scrape Web Pages
def scrape_websites(url, api_key=FIRE_CRAWL_API_KEY, mode="scrape"):
    loader = FireCrawlLoader(url=url, api_key=api_key, mode=mode)
    return loader.load()

# Function to Create Chunks
def create_chunks(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
    return text_splitter.split_documents(documents)

# Function to Initialize Embedding Model
def get_embedding_model():
    return GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# Function to Store Vectors
def store_in_vector_db(chunks):
    embeddings = get_embedding_model()
    faiss_db = FAISS.from_documents(chunks, embeddings)
    faiss_db.save_local(FAISS_DB_PATH)
    return faiss_db

# Function to Load Vector Store
def load_vector_db():
    if not os.path.exists(FAISS_DB_PATH) or not os.listdir(FAISS_DB_PATH):
        return None
    embeddings = get_embedding_model()
    return FAISS.load_local(FAISS_DB_PATH, embeddings,allow_dangerous_deserialization=True)

# Function to Retrieve Documents
def retrieve_docs(query, faiss_db):
    if faiss_db is None:
        return []
    return faiss_db.similarity_search(query)

# Function to Extract Context
def get_context(documents):
    return "\n\n".join([doc.page_content.strip() for doc in documents])

# Function to Answer Queries
def answer_query(query, documents):
    context = get_context(documents)
    if not context:
        return "I'm sorry, but I couldn't find relevant information in the provided context."
    
    prompt_template = """
    Carefully analyze the provided context and use only the given information to answer the user's question.  
    - If the answer is not present in the context, clearly state that you do not know.  
    - Do not make assumptions, add extra information, or generate responses beyond the provided details.  
    - Ensure numerical values, prices, and discounts are correctly interpreted. For example, if a price is given with a discount, clearly indicate the original and discounted prices in the response.  
    - Keep the answer concise, relevant, and factually accurate.  

    ---
    **Question:** {question}  
    **Context:**  
    {context}  

    **Answer:**  
    """

    
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = LLMChain(llm=llm_model, prompt=prompt)
    response = chain.run(question=query, context=context)

    # Removing the meta Part
    return response.content if hasattr(response, 'content') else str(response)

# Sidebar Inputs
st.sidebar.header("🔍 Scrape & Store Data")
url = st.sidebar.text_input("Enter Website URL", placeholder="https://example.com")
if st.sidebar.button("Scrape & Store"):
    if url:
        with st.spinner("Scraping the website..."):
            docs = scrape_websites(url)
            chunks = create_chunks(docs)
            store_in_vector_db(chunks)
            st.sidebar.success("✅ Data successfully stored in vector database!")
    else:
        st.sidebar.error("⚠️ Please enter a valid URL!")



# Query Section
st.header("📝 Ask Questions Based on Scraped Data")
query = st.text_input("Enter your question", placeholder="What information does the website provide?")
if st.button("Get Answer"):
    if query:
        faiss_db = load_vector_db()
        retrieved_docs = retrieve_docs(query, faiss_db)
        answer = answer_query(query, retrieved_docs)
        st.write("### 🤖 AI Answer:")
        st.success(answer)
    else:
        st.warning("⚠️ Please enter a question!")
