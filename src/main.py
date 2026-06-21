import os
import chromadb
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from pypdf import PdfReader

# -----------------------------
# CONFIG
# -----------------------------
load_dotenv()

import streamlit as st

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    api_key = st.secrets.get("GEMINI_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

DATA_DIR = "data"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# -----------------------------
# PDF READING
# -----------------------------
def read_pdfs():
    docs = []

    if not os.path.exists(DATA_DIR):
        return docs

    for file in os.listdir(DATA_DIR):
        if file.endswith(".pdf"):

            pdf_path = os.path.join(DATA_DIR, file)

            reader = PdfReader(pdf_path)

            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()

                if text:
                    docs.append({
                        "text": text,
                        "source": file,
                        "page": page_num + 1
                    })

    return docs


# -----------------------------
# CHUNKING
# -----------------------------
def chunk_text(text):
    chunks = []

    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE

        chunks.append(text[start:end])

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


# -----------------------------
# BUILD DATABASE
# -----------------------------
def build_database(collection):

    docs = read_pdfs()

    all_chunks = []

    for doc in docs:
        chunks = chunk_text(doc["text"])

        for chunk in chunks:
            all_chunks.append({
                "text": chunk,
                "source": doc["source"],
                "page": doc["page"]
            })

    if len(all_chunks) == 0:
        return

    collection.add(
        documents=[c["text"] for c in all_chunks],
        ids=[f"chunk_{i}" for i in range(len(all_chunks))],
        metadatas=[
            {
                "source": c["source"],
                "page": c["page"]
            }
            for c in all_chunks
        ]
    )


# -----------------------------
# CHROMADB
# -----------------------------
client = chromadb.PersistentClient(
    path="db"
)

collection = client.get_or_create_collection(
    name="document_knowledge_base"
)

# Auto build DB if empty
if collection.count() == 0:
    build_database(collection)

# -----------------------------
# UI
# -----------------------------
st.title("📄 Document Q&A Bot")

question = st.text_input(
    "Ask a question about your documents"
)

if st.button("Submit"):

    if question.strip() == "":
        st.warning("Please enter a question.")
        st.stop()

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

If the answer is not found in the context, reply:

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