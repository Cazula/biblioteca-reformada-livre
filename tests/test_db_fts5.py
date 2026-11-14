"""Testes da camada de persistência SQLite e motor FTS5."""

from pathlib import Path
import pytest

from biblioteca_reformada.models import Verse
from biblioteca_reformada.db import (
    init_db,
    insert_verses_batch,
    search_fts,
    reindex_fts,
    get_stats
)


@pytest.fixture
def memory_db():
    conn = init_db(":memory:")
    yield conn
    conn.close()


def test_db_init_creates_tables(memory_db):
    cur = memory_db.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {r[0] for r in cur.fetchall()}
    assert "verses" in tables
    assert "verses_fts" in tables
    assert "documents" in tables
    assert "system_metadata" in tables


def test_insert_and_fts_search(memory_db):
    verses = [
        Verse(book="3 João", chapter=1, verse=3, text="Porque muito me alegrei quando os irmãos vieram e testificaram da tua verdade, como tu andas na verdade.", version_id="BLIVRE"),
        Verse(book="3 João", chapter=1, verse=4, text="Não tenho maior alegria do que esta: a de ouvir que os meus filhos andam na verdade.", version_id="BLIVRE"),
        Verse(book="Gênesis", chapter=1, verse=1, text="No princípio criou Deus os céus e a terra.", version_id="BLIVRE", testament="AT"),
    ]
    inserted = insert_verses_batch(memory_db, verses)
    assert inserted == 3

    # Busca por palavra exata
    results = search_fts(memory_db, "verdade")
    assert len(results) == 2
    assert all("verdade" in r.text.lower() for r in results)

    # Busca por expressão composta
    results_comp = search_fts(memory_db, "princípio criou")
    assert len(results_comp) == 1
    assert results_comp[0].book == "Gênesis"


def test_reindex_fts(memory_db):
    verses = [
        Verse(book="Romanos", chapter=8, verse=1, text="Portanto, agora nenhuma condenação há para os que estão em Cristo Jesus.", version_id="BLIVRE"),
    ]
    insert_verses_batch(memory_db, verses)
    reindexed = reindex_fts(memory_db)
    assert reindexed == 1

    res = search_fts(memory_db, "condenação")
    assert len(res) == 1
    assert res[0].book == "Romanos"
    assert res[0].chapter == 8
    assert res[0].verse == 1


def test_stats(memory_db):
    verses = [
        Verse(book="3 João", chapter=1, verse=1, text="O presbítero ao amado Gaio...", version_id="BLIVRE"),
        Verse(book="3 João", chapter=1, verse=2, text="Amado, desejo que te vá bem...", version_id="BLIVRE"),
    ]
    insert_verses_batch(memory_db, verses)
    stats = get_stats(memory_db)
    assert stats["total_verses"] == 2
    assert stats["total_books"] == 1
    assert stats["fts_indexed_rows"] == 2
    assert stats["verses_by_version"].get("BLIVRE") == 2
