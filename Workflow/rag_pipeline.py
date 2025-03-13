from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
from langchain.chains import LLMChain

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize LLM model
llm_model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=GOOGLE_API_KEY,temperature=0.2)

# Function to retrieve relevant documents
def retrieve_docs(query, faiss_db):
    if faiss_db is None:
        return []
    return faiss_db.similarity_search(query)

# Function to extract context from retrieved documents
def get_context(documents):
    return "\n\n".join([doc.page_content.strip() for doc in documents])

# LLM Model for answering queries
llm_model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=GOOGLE_API_KEY)

# Answer question using context
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
    return response.content if hasattr(response, 'content') else str(response)


