"""Testes de execução de busca textual e formatação de citações."""

from pathlib import Path
import pytest

from biblioteca_reformada.models import SearchResult
from biblioteca_reformada.search import format_search_results, execute_search
from biblioteca_reformada.db import init_db, insert_verses_batch
from biblioteca_reformada.importer import parse_book_json


def test_format_search_results():
    results = [
        SearchResult(book="3 João", chapter=1, verse=4, text="Não tenho maior alegria do que esta: a de ouvir que os meus filhos andam na verdade.", version_id="BLIVRE"),
    ]
    formatted = format_search_results("verdade", results)
    assert "3 João 1:4 (BLIVRE)" in formatted
    assert "Não tenho maior alegria" in formatted
    assert "Resultados encontrados: 1" in formatted


def test_execute_search_real():
    root = Path(__file__).resolve().parent.parent
    sample_json = root / "corpus" / "approved" / "bible" / "blivre" / "64-3-joao.json"

    conn = init_db(":memory:")
    verses = parse_book_json(sample_json)
    insert_verses_batch(conn, verses)

    # Busca pela palavra "verdade"
    results = execute_search(conn, "verdade")
    assert len(results) > 0
    # Verifica que 3 João 1:4 está entre os resultados
    assert any(r.chapter == 1 and r.verse == 4 for r in results)

    # Busca por citação exata
    results_paz = execute_search(conn, "paz")
    assert any(r.verse == 14 for r in results_paz)
    conn.close()
