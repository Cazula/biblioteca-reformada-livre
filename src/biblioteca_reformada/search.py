"""Módulo de execução e formatação de busca textual com citações exatas."""

import sqlite3
from typing import List, Optional
from biblioteca_reformada.models import SearchResult
from biblioteca_reformada.db import search_fts


def execute_search(conn: sqlite3.Connection, query: str, limit: int = 20) -> List[SearchResult]:
    """Executa a busca FTS5 e retorna a lista de resultados."""
    return search_fts(conn, query, limit=limit)


def format_search_results(query: str, results: List[SearchResult]) -> str:
    """Formata os resultados da busca em formato de exibição legível com referências exatas."""
    sep = "=" * 80
    lines = [
        sep,
        "BIBLIOTECA REFORMADA LIVRE — BUSCA TEXTUAL FTS5",
        f'Consulta: "{query}" | Resultados encontrados: {len(results)}',
        sep,
    ]

    if not results:
        lines.append("Nenhum versículo ou trecho encontrado para os termos informados.")
        lines.append(sep)
        return "\n".join(lines)

    for i, res in enumerate(results, start=1):
        lines.append(f"[{i}] {res.reference} ({res.version_id})")
        lines.append(f'    "{res.text}"')
        lines.append("")

    lines.append(sep)
    return "\n".join(lines)
