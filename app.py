import streamlit as st
from Workflow.scrape import scrape_websites
from Workflow.vectorstore import create_chunks,store_in_vector_db,load_vector_db
from Workflow.rag_pipeline import retrieve_docs,answer_query





# Streamlit App UI
st.set_page_config(page_title="Web Scraper & QA Chatbot", layout="wide")
st.title("🌍 Web Scraper & QA Chatbot")



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