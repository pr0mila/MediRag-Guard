import hashlib
from typing import List, Dict, Optional
from langchain.schema import Document
from config import DOC_CHUNKS # Import DOC_CHUNKS from config

# Pre-calculate hashes for easier CONTEXT_TREE definition
# This maps a hash to its original chunk content. This is used in rag_system.py for display.
CHUNK_HASHES = {hashlib.sha256(chunk.encode()).hexdigest(): chunk for chunk in DOC_CHUNKS}

# The CONTEXT_TREE Structure
# This dictionary represents the hierarchical knowledge structure.
# Leaf nodes (the innermost lists) contain the SHA256 hashes of the corresponding document chunks.
CONTEXT_TREE = {
    "Healthcare Regulations": {
        "United States": {
            # CORRECTED: Directly store the hash, do NOT use chunk_hashes[...] here
            "HIPAA": [hashlib.sha256(DOC_CHUNKS[1].encode()).hexdigest()]
        },
        "European Union": {
            # CORRECTED: Directly store the hash
            "GDPR": [hashlib.sha256(DOC_CHUNKS[2].encode()).hexdigest()]
        },
        "General Privacy Principles": [
            # CORRECTED: Directly store the hash
            hashlib.sha256(DOC_CHUNKS[0].encode()).hexdigest()
        ]
    },
    "Data Security Measures": {
        "Technical Safeguards": [
            # CORRECTED: Directly store the hash
            hashlib.sha256(DOC_CHUNKS[4].encode()).hexdigest()
        ],
        "Risks and Consequences": [
            # CORRECTED: Directly store the hash
            hashlib.sha256(DOC_CHUNKS[3].encode()).hexdigest()
        ],
        "Common Threats": [
            # CORRECTED: Directly store the hash for the new chunk
            hashlib.sha256(DOC_CHUNKS[6].encode()).hexdigest()
        ]
    },
    "Data Management Lifecycle": { # New top-level category
        "Data Flow and Stages": [
            # CORRECTED: Directly store the hash for the new chunk
            hashlib.sha256(DOC_CHUNKS[5].encode()).hexdigest()
        ],
        "Risk Assessment": [
            # CORRECTED: Directly store the hash for the new chunk (PIAs)
            hashlib.sha256(DOC_CHUNKS[7].encode()).hexdigest()
        ],
        "Data Anonymization": [ # New sub-category
            # CORRECTED: Directly store the hash for the new chunk (De-identification)
            hashlib.sha256(DOC_CHUNKS[8].encode()).hexdigest()
        ]
    },
    "Emerging Technologies": { # New top-level category
        "AI and Blockchain Impacts": [
            # CORRECTED: Directly store the hash for the new chunk
            hashlib.sha256(DOC_CHUNKS[9].encode()).hexdigest()
        ]
    }
}

def find_leaf_node(chunk_hash: str) -> Optional[List[str]]:
    """
    Recursively searches the CONTEXT_TREE to find the path to the leaf node
    containing the given chunk_hash.

    Args:
        chunk_hash: The SHA256 hash of a document chunk.

    Returns:
        A list of strings representing the path from the root to the leaf node,
        or None if the hash is not found.
    """
    def search_tree(node, path=None):
        if path is None:
            path = []

        if isinstance(node, dict):
            for key, value in node.items():
                result = search_tree(value, path + [key])
                if result:
                    return result
        elif isinstance(node, list):
            if chunk_hash in node:
                return path
        return None

    return search_tree(CONTEXT_TREE, [])

def get_broader_context(leaf_path: List[str]) -> Dict:
    """
    Traverses up the context tree from the given leaf path to gather broader context.
    This includes siblings at each level of the path.

    Args:
        leaf_path: A list of strings representing the path to a leaf node.

    Returns:
        A dictionary where keys are levels in the path, and values are lists
        of sibling names at that level.
    """
    context = {}
    current_node = CONTEXT_TREE

    for i, level in enumerate(leaf_path):
        if isinstance(current_node, dict) and level in current_node:
            context[level] = []
            for key, value in current_node.items():
                if key != level:
                    if isinstance(value, dict):
                        context[level].extend(value.keys())
                    elif isinstance(value, list):
                        context[level].extend(value)
            current_node = current_node[level]
        else:
            break
    return context