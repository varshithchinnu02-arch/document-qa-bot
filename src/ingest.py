from pypdf import PdfReader
import os

DATA_DIR = "data"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def read_pdfs():
    docs = []

    for file in os.listdir(DATA_DIR):
        if file.endswith(".pdf"):
            reader = PdfReader(os.path.join(DATA_DIR, file))

            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()

                if text:
                    docs.append({
                        "text": text,
                        "source": file,
                        "page": page_num + 1
                    })

    return docs


def chunk_text(text):
    chunks = []

    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE

        chunks.append(text[start:end])

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


if __name__ == "__main__":

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

    print("Total Chunks:", len(all_chunks))

    print(all_chunks[0])