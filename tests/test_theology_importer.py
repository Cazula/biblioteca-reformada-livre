"""Testes automatizados do importador de obras teológicas clássicas e motor FTS5."""

from pathlib import Path
import pytest

from biblioteca_reformada.db import init_db
from biblioteca_reformada.theology_importer import (
    init_theology_tables,
    import_neuu_classic,
    search_theological
)


@pytest.fixture
def memory_db():
    conn = init_db(":memory:")
    init_theology_tables(conn)
    yield conn
    conn.close()


def test_import_neuu_classic_athanasius(memory_db):
    root = Path(__file__).resolve().parent.parent
    athanasius_json = root / "data" / "sources" / "neuu-classics" / "data" / "02_translated" / "pt" / "athanasius" / "incarnation.json"
    
    if not athanasius_json.exists():
        pytest.skip("Dataset local de Atanásio não presente em data/sources/")

    doc, total_paras = import_neuu_classic(athanasius_json, memory_db)
    assert doc.author == "Santo Atanásio"
    assert "Encarnação do Verbo" in doc.title
    assert doc.tradition == "Patrística"
    assert doc.license == "CC-BY-4.0"
    assert total_paras > 0
    assert doc.paragraphs_count == total_paras

    cur = memory_db.execute("SELECT COUNT(*) FROM theological_paragraphs WHERE document_id = ?", (doc.id,))
    assert cur.fetchone()[0] == total_paras

    results = search_theological(memory_db, "Verbo")
    assert len(results) > 0
    primeiro = results[0]
    assert "Atanásio" in primeiro.author
    assert "Encarnação" in primeiro.title
    assert "§" in primeiro.citation
    assert len(primeiro.text) > 20

    results_comp = search_theological(memory_db, "renovação da criação")
    assert len(results_comp) > 0
    assert any("renovação da criação" in r.text.lower() for r in results_comp)


def test_import_neuu_classic_lawrence(memory_db):
    root = Path(__file__).resolve().parent.parent
    lawrence_json = root / "data" / "sources" / "neuu-classics" / "data" / "02_translated" / "pt" / "lawrence" / "practice.json"
    
    if not lawrence_json.exists():
        pytest.skip("Dataset local de Irmão Lawrence não presente em data/sources/")

    doc, total_paras = import_neuu_classic(lawrence_json, memory_db)
    assert any(name in doc.author for name in ("Lawrence", "Irmão", "Irmao", "Lourenco"))
    assert total_paras > 0

    results = search_theological(memory_db, "presença")
    assert len(results) > 0


def test_search_theological_unbalanced_quotes(memory_db):
    root = Path(__file__).resolve().parent.parent
    athanasius_json = root / "data" / "sources" / "neuu-classics" / "data" / "02_translated" / "pt" / "athanasius" / "incarnation.json"
    if not athanasius_json.exists():
        pytest.skip("Dataset local de Atanásio não presente")

    import_neuu_classic(athanasius_json, memory_db)

    res = search_theological(memory_db, 'Verbo"')
    assert isinstance(res, list)

    res2 = search_theological(memory_db, '""criação')
    assert isinstance(res2, list)


def test_theology_importer_file_not_found(memory_db):
    with pytest.raises(FileNotFoundError):
        import_neuu_classic(Path("caminho/inexistente.json"), memory_db)
