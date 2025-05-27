import os
from dotenv import load_dotenv # Import load_dotenv

# Ensure .env variables are loaded FIRST
load_dotenv()
# ChromaDB Configuration
CHROMA_PERSIST_DIR = "./chroma_db_demo"
COLLECTION = "healthcare_data_privacy"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Groq API Configuration
# It's recommended to load these from environment variables for security
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME")

# Example Document Chunks (for initial ingestion/demo purposes)
# In a real application, these would come from a data source
DOC_CHUNKS = [
    "Healthcare data privacy refers to the protection of sensitive patient information from unauthorized access, use, or disclosure. This includes medical records, billing information, and any personal health information (PHI).",
    "HIPAA (Health Insurance Portability and Accountability Act) is a key legislation in the United States that sets standards for the protection of patient health information. It outlines rules for covered entities like healthcare providers and health plans.",
    "GDPR (General Data Protection Regulation) is a data protection law in the European Union that impacts healthcare organizations handling data of EU citizens. It emphasizes consent, transparency, and data minimization.",
    "Data breaches in healthcare can lead to significant financial penalties, reputational damage, and loss of patient trust. Protecting patient data is paramount for ethical and legal compliance.",
    "Encryption and access controls are essential technical safeguards for healthcare data. Data should be encrypted both in transit and at rest, and access should be granted only on a 'need-to-know' basis.",
    "The data lifecycle in healthcare involves creation, collection, processing, storage, use, sharing, retention, and ultimate destruction of patient information. Each stage requires specific privacy and security considerations.",
    "Common threats to healthcare data include phishing attacks, ransomware, insider threats, and lost or stolen devices. Organizations must implement robust defenses against these vectors.",
    "Privacy Impact Assessments (PIAs) are crucial tools used to identify and mitigate privacy risks associated with new projects, systems, or processes that involve personal health information.",
    "De-identification of health data involves removing or obscuring identifiers that could link information to a specific individual. This allows data to be used for research or public health without compromising privacy.",
    "Emerging technologies like Artificial Intelligence (AI) and blockchain present both opportunities and challenges for healthcare data privacy. Careful governance frameworks are needed to leverage their benefits while mitigating risks."
]