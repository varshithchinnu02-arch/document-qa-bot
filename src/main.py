import os
import chromadb
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

client = chromadb.PersistentClient(
    path="db"
)

collection = client.get_collection(
    "document_knowledge_base"
)

st.title("📄 Document Q&A Bot")

question = st.text_input(
    "Ask a question about your documents"
)

if st.button("Submit"):

    results = collection.query(
        query_texts=[question],
        n_results=3
    )

    context = "\n\n".join(
        results["documents"][0]
    )

    prompt = f"""
    Answer only from context.

    If answer not found, say:

    I cannot find the answer in the provided documents.

    Context:
    {context}

    Question:
    {question}
    """

    response = model.generate_content(
        prompt
    )

    st.subheader("Answer")
    st.write(response.text)

    st.subheader("Sources")

    for meta in results["metadatas"][0]:
        st.write(
            f"{meta['source']} | Page {meta['page']}"
        )