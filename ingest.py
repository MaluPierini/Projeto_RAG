import sys
from collections import defaultdict
from pathlib import Path

from app.document_processing.loader import carregar_documentos
from app.document_processing.splitter import dividir_chunks
from app.embeddings.embedding import get_embeddings
from app.vectorstore.chroma_db import banco_existe, criar_banco, limpar_banco


def limpar_chunks(chunks):
    """Remove caracteres inválidos dos trechos e descarta os que ficarem vazios."""
    limpos = []
    resumo = defaultdict(lambda: {"total": 0, "alterados": 0, "descartados": 0, "removidos": 0})

    for chunk in chunks:
        arquivo = Path(chunk.metadata.get("source", "?")).name
        original = chunk.page_content if isinstance(chunk.page_content, str) else ""
        texto = original.encode("utf-8", "ignore").decode("utf-8").replace("\x00", "")

        dados = resumo[arquivo]
        dados["total"] += 1
        dados["removidos"] += len(original) - len(texto)

        if not texto.strip():
            dados["descartados"] += 1
            continue
        if texto != original:
            dados["alterados"] += 1

        chunk.page_content = texto
        limpos.append(chunk)

    print(f"\nTrechos: {len(chunks)} gerados, {len(limpos)} mantidos, {len(chunks) - len(limpos)} descartados\n")
    print(f"{'total':>6} {'alter.':>6} {'desc.':>6} {'carac.':>7}  arquivo")
    for arquivo, d in sorted(resumo.items()):
        if d["alterados"] or d["descartados"]:
            print(f"{d['total']:6d} {d['alterados']:6d} {d['descartados']:6d} {d['removidos']:7d}  {arquivo}")

    return limpos


def criar_base_vetorial(forcar=False):

    embeddings = get_embeddings()

    if banco_existe(embeddings):
        if not forcar:
            print("Banco vetorial já existe. Nada a fazer (use --force para reindexar).")
            return
        limpar_banco(embeddings)

    documentos = carregar_documentos()

    chunks = dividir_chunks(documentos)

    chunks = limpar_chunks(chunks)

    criar_banco(chunks, embeddings)

    print(f"Banco vetorial criado com sucesso! ({len(chunks)} chunks)")


if __name__ == "__main__":
    criar_base_vetorial(forcar="--force" in sys.argv)