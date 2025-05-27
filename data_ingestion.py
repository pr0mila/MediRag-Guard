import os
import hashlib
import chromadb
from langchain.schema import Document
from dotenv import load_dotenv
from config import CHROMA_PERSIST_DIR, COLLECTION, DOC_CHUNKS

def ingest_documents():
    """
    Initializes ChromaDB and adds document chunks to the collection.
    Checks for existing documents to avoid duplicates.
    """
    load_dotenv() # Ensure .env variables are loaded

    if not os.path.exists(CHROMA_PERSIST_DIR):
        os.makedirs(CHROMA_PERSIST_DIR)
        print(f"Created ChromaDB persistent directory: {CHROMA_PERSIST_DIR}")

    try:
        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        collection = client.get_or_create_collection(COLLECTION)
        print(f"ChromaDB collection '{COLLECTION}' ready.")

        documents_to_add = []
        ids_to_add = []
        metadatas_to_add = []

        # Create Langchain Document objects and generate hashes
        # Add a dummy metadata field as ChromaDB requires non-empty metadata dicts
        langchain_docs = [
            Document(page_content=chunk, metadata={"source_chunk_id": f"chunk_{i+1}"})
            for i, chunk in enumerate(DOC_CHUNKS)
        ]

        # Check for existing IDs to avoid re-adding documents
        existing_ids = set()
        try:
            all_ids_in_collection = collection.get(ids=None, include=[])['ids']
            existing_ids = set(all_ids_in_collection)
        except Exception as e:
            print(f"Note: Could not retrieve existing IDs from collection (may be empty or version issue): {e}")

        for doc in langchain_docs:
            doc_id = hashlib.sha256(doc.page_content.encode()).hexdigest()
            if doc_id not in existing_ids:
                documents_to_add.append(doc.page_content)
                ids_to_add.append(doc_id)
                metadatas_to_add.append(doc.metadata)

        if documents_to_add:
            collection.add(
                documents=documents_to_add,
                metadatas=metadatas_to_add,
                ids=ids_to_add
            )
            print(f"Successfully added {len(documents_to_add)} new documents to ChromaDB.")
        else:
            print(f"All sample documents already exist in ChromaDB collection '{COLLECTION}'. No new documents added.")

    except Exception as e:
        print(f"\n--- ERROR DURING CHROMADB SETUP ---")
        print(f"An error occurred while initializing or adding to ChromaDB: {e}")
        print("Please ensure `chromadb` and `sentence-transformers` are installed.")
        print("Exiting.")
        exit()

if __name__ == "__main__":
    ingest_documents()