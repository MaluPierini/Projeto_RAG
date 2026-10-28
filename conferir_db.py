from collections import Counter
from pathlib import Path

import chromadb

cliente = chromadb.PersistentClient(path="db")

for item in cliente.list_collections():
    nome = item if isinstance(item, str) else item.name
    colecao = cliente.get_collection(nome)
    metadados = colecao.get(include=["metadatas"])["metadatas"]
    por_arquivo = Counter(Path(m.get("source", "?")).name for m in metadados)

    print(f"\nColeção: {nome}")
    print(f"Total de trechos: {colecao.count()}")
    print(f"Documentos distintos: {len(por_arquivo)}\n")
    for arquivo, quantidade in sorted(por_arquivo.items()):
        print(f"{quantidade:6d}  {arquivo}")

