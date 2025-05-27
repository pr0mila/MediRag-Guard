import hashlib
import chromadb
from typing import List, Dict, Optional
from langchain.schema import Document
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

from config import CHROMA_PERSIST_DIR, COLLECTION, GROQ_API_KEY, GROQ_MODEL_NAME
from context_tree import find_leaf_node, get_broader_context, CHUNK_HASHES

class ContextTreeRAG:
    """
    Implements a Retrieval-Augmented Generation (RAG) system
    that leverages a hierarchical context tree for expanded context.
    """
    def __init__(self):
        load_dotenv() # Load environment variables

        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set. Please set it in your .env file or as an environment variable.")
        if not GROQ_MODEL_NAME:
            raise ValueError("GROQ_MODEL_NAME is not set. Please set it in your .env file or as an environment variable.")

        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        self.collection = client.get_or_create_collection(COLLECTION)

        self.llm = ChatGroq(
            model_name=GROQ_MODEL_NAME,
            api_key=GROQ_API_KEY,
            temperature=0.7,
            max_tokens=250,
            top_p=1.0
        )

    def _generate_hash(self, text: str) -> str:
        """Generates a SHA256 hash for the given text content."""
        return hashlib.sha256(text.encode()).hexdigest()

    def retrieve_chunks(self, query: str, k: int = 3) -> List[Document]:
        """
        Retrieves the most relevant document chunks from ChromaDB based on the query.
        """
        print(f"\n--- Step 1: Retrieving {k} relevant chunks from ChromaDB ---")
        print(f"Querying ChromaDB with: '{query}'")

        results = self.collection.query(
            query_texts=[query],
            n_results=k,
            include=['documents', 'metadatas', 'distances']
        )

        retrieved_docs = []
        if results and results.get("documents") and results.get("metadatas"):
            for i in range(len(results["documents"][0])):
                page_content = results["documents"][0][i]
                metadata = results["metadatas"][0][i] if results["metadatas"][0][i] else {}
                retrieved_docs.append(Document(page_content=page_content, metadata=metadata))

        print(f"Retrieved {len(retrieved_docs)} chunks from ChromaDB.")
        return retrieved_docs

    def expand_context(self, chunks: List[Document]) -> Dict:
        """
        Expands the context for each retrieved chunk by finding its place
        in the CONTEXT_TREE and identifying broader hierarchical relationships.
        """
        print("\n--- Step 2: Expanding context using the hierarchical tree structure ---")
        expanded_context = {}

        for chunk in chunks:
            chunk_hash = self._generate_hash(chunk.page_content)
            leaf_path = find_leaf_node(chunk_hash)

            if leaf_path:
                broader_context = get_broader_context(leaf_path)
                expanded_context[chunk_hash] = {
                    "chunk": chunk,
                    "path": leaf_path,
                    "broader_context": broader_context
                }
                print(f"  - Chunk found in tree: {chunk_hash[:10]}... (Path: {' → '.join(leaf_path)})")
            else:
                print(f"  - Chunk not found in CONTEXT_TREE: {chunk_hash[:10]}... (No broader context expansion)")

        return expanded_context

    def generate_prompt(self, query: str, expanded_context: Dict) -> str:
        """
        Constructs a comprehensive prompt for the LLM, incorporating the original query,
        retrieved chunks, and their expanded hierarchical context.
        """
        print("\n--- Step 3: Generating comprehensive prompt for the LLM ---")
        prompt_parts = [
            "You are an expert assistant answering questions based on the following context:",
            "\n=== QUERY ===\n",
            query,
            "\n=== RELEVANT CONTEXT ===\n"
        ]

        if not expanded_context:
            prompt_parts.append(
                "**No specific relevant context chunks were found to directly answer this question.**\n"
                "You should use your general knowledge to answer the question, but explicitly state that "
                "the answer is not derived from the provided context. If the question is nonsensical or "
                "you cannot answer it, state that clearly."
            )
        else:
            for chunk_hash, chunk_data in expanded_context.items():
                chunk = chunk_data["chunk"]
                path = " → ".join(chunk_data["path"])
                broader = chunk_data["broader_context"]

                prompt_parts.append(f"\n**Document Chunk** (Source: {path}):")
                prompt_parts.append(chunk.page_content)
                if chunk.metadata:
                    prompt_parts.append("\n**Metadata**:")
                    prompt_parts.append(str(chunk.metadata))

                if broader:
                    prompt_parts.append("\n**Broader Context from Hierarchy**:")
                    for level, siblings in broader.items():
                        if siblings:
                            display_siblings = []
                            for s in siblings:
                                display_siblings.append(CHUNK_HASHES.get(s, s[:50] + "...") if isinstance(s, str) else str(s))
                            prompt_parts.append(f"- At '{level}' level: Related to {', '.join(display_siblings)}")
                        else:
                            prompt_parts.append(f"- At '{level}' level: No explicit related topics found.")
                else:
                    prompt_parts.append("\n**Broader Context from Hierarchy**: No broader context derived for this chunk.")

        prompt_parts.append("\n=== INSTRUCTIONS ===\n")
        prompt_parts.append(
            "1. **If relevant context is provided:** Answer the query accurately and comprehensively using *only* the provided context.\n"
            "   - When relevant, acknowledge the source hierarchy (e.g., 'According to the section on X within Y...').\n"
            "   - If different chunks provide conflicting information, explicitly note the conflict and explain possible reasons or perspectives.\n"
            "   - Explain how information from a specific chunk fits into its broader hierarchical context.\n"
            "2. **If *no* relevant context is provided:** Clearly state that the answer is based on your general knowledge and not the provided context. Then, answer the question to the best of your ability. If you cannot answer the question, state that you don't have enough information.\n"
            "3. Do not introduce external information or make assumptions beyond the given context unless explicitly stated in instruction 2.\n"
            "4. Your response should be helpful and informative."
        )

        final_prompt = "\n".join(prompt_parts)
        print("Prompt generated. Length:", len(final_prompt), "characters.")
        return final_prompt

    @staticmethod
    def until_last_stop(text: str) -> str:
        """Truncates the text at the last full stop (.) and returns it."""
        last_stop_index = text.rfind('.')
        if last_stop_index != -1:
            return text[:last_stop_index + 1]
        else:
            return text

    def ask_question(self, query: str) -> str:
        """
        Executes the full RAG pipeline: retrieve, expand context, generate prompt, and query LLM.
        """
        chunks = self.retrieve_chunks(query)
        expanded_context = self.expand_context(chunks)
        prompt = self.generate_prompt(query, expanded_context)

        print("\n--- Step 4: Sending prompt to LLM and getting response ---")
        response = self.llm.invoke(prompt)
        print("LLM response received.")

        final_response = ContextTreeRAG.until_last_stop(response.content)
        return final_response