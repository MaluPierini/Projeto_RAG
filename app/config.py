PDF_DIRECTORY = "data/pdfs"

CHROMA_DIRECTORY = "db"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

EMBEDDING_MODEL = "BAAI/bge-m3"

TOP_K = 5

SIMILARITY_THRESHOLD = 0.30

LLM_PROVIDER = "ollama"

# LLM_MODEL = "phi3:latest"

LLM_MODEL = "phi3:latest"

# Máximo de tokens gerados por resposta. Corta loops de geração antes de
# estourarem a janela de contexto do Ollama (4096 tokens por padrão)
LLM_MAX_TOKENS = 1500
