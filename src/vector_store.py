import chromadb

client = chromadb.PersistentClient(path="db")

collection = client.get_or_create_collection(
    name="document_knowledge_base"
)

print("Collection Ready")