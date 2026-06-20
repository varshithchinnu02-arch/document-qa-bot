import os
import chromadb
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Gemini Setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

# ChromaDB
client = chromadb.PersistentClient(path="db")

collection = client.get_collection(
    "document_knowledge_base"
)

question = input("Ask a question: ")

# Retrieve relevant chunks
results = collection.query(
    query_texts=[question],
    n_results=3
)

context = "\n\n".join(
    results["documents"][0]
)

prompt = f"""
You are a document assistant.

Answer ONLY from the provided context.

If the answer is not available in the context,
say:

"I cannot find the answer in the provided documents."

Context:
{context}

Question:
{question}
"""

response = model.generate_content(prompt)

print("\nANSWER:\n")
print(response.text)

print("\nSOURCES:\n")

for meta in results["metadatas"][0]:
    print(
        f"{meta['source']} | Page {meta['page']}"
    )