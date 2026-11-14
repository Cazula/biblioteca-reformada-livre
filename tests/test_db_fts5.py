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


def test_conflict_resolution_and_update(memory_db):
    # Insere versículo inicial
    v1 = [Verse(book="Romanos", chapter=1, verse=1, text="Texto original", version_id="BLIVRE")]
    insert_verses_batch(memory_db, v1)
    res1 = search_fts(memory_db, "original")
    assert len(res1) == 1

    # Reinsere com texto corrigido
    v2 = [Verse(book="Romanos", chapter=1, verse=1, text="Texto corrigido e atualizado", version_id="BLIVRE")]
    insert_verses_batch(memory_db, v2)

    # Verifica que o texto foi atualizado no relacional e no FTS5 sem duplicatas
    res_old = search_fts(memory_db, "original")
    assert len(res_old) == 0

    res_new = search_fts(memory_db, "corrigido")
    assert len(res_new) == 1
    assert res_new[0].text == "Texto corrigido e atualizado"

    cur = memory_db.execute("SELECT COUNT(*) FROM verses WHERE book='Romanos' AND chapter=1 AND verse=1")
    assert cur.fetchone()[0] == 1


def test_search_fts_unbalanced_quotes(memory_db):
    verses = [
        Verse(book="3 João", chapter=1, verse=3, text="Testificaram da tua verdade", version_id="BLIVRE"),
    ]
    insert_verses_batch(memory_db, verses)

    # Consulta com aspas desbalanceadas não deve lançar OperationalError
    res1 = search_fts(memory_db, 'verdade"')
    assert isinstance(res1, list)

    res2 = search_fts(memory_db, '""verdade')
    assert isinstance(res2, list)


def test_search_fts_negative_limit(memory_db):
    verses = [
        Verse(book="3 João", chapter=1, verse=1, text="Gaio amado", version_id="BLIVRE"),
    ]
    insert_verses_batch(memory_db, verses)

    # Limite negativo é normalizado para o padrão positivo
    res = search_fts(memory_db, "amado", limit=-5)
    assert len(res) == 1


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


def test_search_fts_missing_table_propagates_error(memory_db):
    import sqlite3
    # Dropar tabela FTS para simular indisponibilidade
    memory_db.execute("DROP TABLE verses_fts")
    with pytest.raises(sqlite3.OperationalError) as exc_info:
        search_fts(memory_db, "qualquer termo")
    assert "no such table" in str(exc_info.value).lower()

