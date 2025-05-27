from data_ingestion import ingest_documents
from rag_system import ContextTreeRAG

def main():
    print("--- Starting MediGuard AI Demo ---")

    # Step 0: Ensure documents are ingested into ChromaDB
    ingest_documents()

    print("\n--- Initializing MediGuard AI system ---")
    rag_system = ContextTreeRAG()

    # --- Run various queries to demonstrate the RAG pipeline ---

    queries = [
        "What are the main regulations protecting healthcare data?",
        "Tell me about technical safeguards for healthcare data.",
        "What is healthcare data privacy?",
        "What are the consequences of data breaches in healthcare?",
        "What is the history of medical informatics in ancient civilizations?", # Out of context
        "Can you explain quantum mechanics in simple terms?", # Out of context
        "What about data security?" # Ambiguous
    ]

    for i, query in enumerate(queries):
        print(f"\nQUERY {i+1}: \"{query}\"")
        answer = rag_system.ask_question(query)
        print(f"\n--- Final Answer for Query {i+1} ---")
        print(answer)
        print("-" * 50)

if __name__ == "__main__":
    main()