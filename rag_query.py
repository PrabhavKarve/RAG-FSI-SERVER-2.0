import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Step 1: Load environment and embedding model
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env")

embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# Step 2: Load vector store
vectorstore = FAISS.load_local(
    ".",
    embeddings=embedding_model,
    allow_dangerous_deserialization=True
)

# retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 10, "fetch_k": 50}
)

# Step 3: Define prompt
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a financial analyst assistant. Use the following financial data to answer the question. 
Be concise, and if the information isn't available, say so.

Context: {context}
Question: {question}
Answer:
"""
)

# Step 4: Create RAG chain
llm = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type_kwargs={"prompt": prompt_template}
)


def run_rag_question(query: str) -> str:
    return qa_chain.run(query)


'''
# Step 5: Ask multiple questions
questions = ["Give me Total Current Assets Infosys for Infosys"]

print("\n📊 Tata Motors Financial Intelligence (RAG):\n")
for q in questions:
    print(f"🟠 Q: {q}")
    answer = qa_chain.run(q)
    print(f"✅ A: {answer}\n")

query = "Total Current Assets Infosys"
docs = vectorstore.similarity_search(query, k=5)

print("🔎 Similarity search results:")
for i, d in enumerate(docs, 1):
    print(f"\nResult {i}:")
    print(d.page_content)
'''

'''
[
    "What was the net profit in FY 2024?",
    "How did revenue change between 2023 and 2024?",
    "What are the total assets in 2024?",
    "Did Tata Motors generate more cash from operations in 2024 compared to 2023?",
    "Is there any indication of debt change from 2023 to 2024?"
]
'''
