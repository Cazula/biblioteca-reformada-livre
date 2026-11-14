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

    # Verifica se os registros foram gravados na tabela relacional
    cur = memory_db.execute("SELECT COUNT(*) FROM theological_paragraphs WHERE document_id = ?", (doc.id,))
    assert cur.fetchone()[0] == total_paras

    # Busca textual FTS5 por termo teológico fundamental
    results = search_theological(memory_db, "Verbo")
    assert len(results) > 0
    primeiro = results[0]
    assert "Atanásio" in primeiro.author
    assert "Encarnação" in primeiro.title
    assert "§" in primeiro.citation
    assert len(primeiro.text) > 20

    # Busca por expressão composta
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

    # Consulta com aspas malformadas não deve quebrar
    res = search_theological(memory_db, 'Verbo"')
    assert isinstance(res, list)

    res2 = search_theological(memory_db, '""criação')
    assert isinstance(res2, list)


def test_theology_importer_file_not_found(memory_db):
    with pytest.raises(FileNotFoundError):
        import_neuu_classic(Path("caminho/inexistente.json"), memory_db)


def test_import_approved_theology_edwards(memory_db):
    root = Path(__file__).resolve().parent.parent
    edwards_json = root / "corpus" / "approved" / "theology" / "edwards-sinners-angry-god.json"
    assert edwards_json.exists(), "Arquivo de Jonathan Edwards deve existir no corpus aprovado"

    doc, total_paras = import_neuu_classic(edwards_json, memory_db)
    assert doc.author == "Jonathan Edwards"
    assert "Pecadores nas Mãos de um Deus Irado" in doc.title
    assert doc.license == "CC-BY-4.0"
    assert total_paras == 20
    assert doc.chapters_count == 3

    # Busca FTS5 por citações características de Edwards
    res = search_theological(memory_db, "aranha")
    assert len(res) > 0
    assert "Jonathan Edwards" in res[0].citation
    assert "aranha" in res[0].text.lower()


def test_import_approved_theology_luther(memory_db):
    root = Path(__file__).resolve().parent.parent
    luther_json = root / "corpus" / "approved" / "theology" / "luther-small-catechism.json"
    assert luther_json.exists(), "Arquivo do Catecismo Menor deve existir no corpus aprovado"

    doc, total_paras = import_neuu_classic(luther_json, memory_db)
    assert "Lutero" in doc.author
    assert "O Catecismo Menor" in doc.title
    assert doc.license == "CC-BY-4.0"
    assert total_paras == 31
    assert doc.chapters_count == 5

    # Busca FTS5 pelos Mandamentos
    res = search_theological(memory_db, "adulterarás")
    assert len(res) > 0
    assert "Mandamento" in res[0].chapter_title


def test_import_approved_theology_anglican_articles(memory_db):
    root = Path(__file__).resolve().parent.parent
    articles_json = root / "corpus" / "approved" / "theology" / "thirty-nine-articles.json"
    assert articles_json.exists(), "Arquivo dos 39 Artigos deve existir no corpus aprovado"

    doc, total_paras = import_neuu_classic(articles_json, memory_db)
    assert "Inglaterra" in doc.author
    assert "Trinta e Nove Artigos" in doc.title
    assert doc.license == "CC-BY-4.0"
    assert total_paras == 19

    # Busca FTS5 por Justificação pela fé só (Artigo XI)
    res = search_theological(memory_db, "justificados somente pela fé")
    assert len(res) > 0
    assert "Artigo XI" in res[0].text


def test_import_approved_theology_baptist_confession_1689(memory_db):
    root = Path(__file__).resolve().parent.parent
    baptist_json = root / "corpus" / "approved" / "theology" / "baptist-confession-1689.json"
    assert baptist_json.exists(), "Arquivo da Confissão de 1689 deve existir no corpus aprovado"

    doc, total_paras = import_neuu_classic(baptist_json, memory_db)
    assert "Batistas" in doc.author
    assert "1689" in doc.title
    assert doc.license == "CC-BY-4.0"
    assert total_paras == 13

    # Busca FTS5 por regra de fé infalível (Capítulo 1)
    res = search_theological(memory_db, "regra suficiente correta e infalível")
    assert len(res) > 0
    assert "Escritura" in res[0].chapter_title


def test_reimport_updates_license_on_conflict(memory_db):
    """Garante que a reimportação atualiza a licença de um documento pré-existente (ON CONFLICT)."""
    root = Path(__file__).resolve().parent.parent
    baptist_json = root / "corpus" / "approved" / "theology" / "baptist-confession-1689.json"
    assert baptist_json.exists()

    doc_id = "baptist:confession-1689:pt"

    # Simula documento antigo cadastrado com licença desatualizada 'Public Domain'
    memory_db.execute("""
        INSERT INTO theological_documents (
            id, work_id, title, author, tradition, category, language,
            license, attribution, chapters_count, paragraphs_count
        ) VALUES (
            ?, 'baptist:confession-1689', 'Confissão 1689',
            'Batistas', 'Reformada', 'Confissões', 'pt', 'Public Domain',
            'Antigo', 1, 1
        )
    """, (doc_id,))
    cur = memory_db.execute("SELECT license FROM theological_documents WHERE id = ?", (doc_id,))
    assert cur.fetchone()[0] == "Public Domain"

    # Reimporta o arquivo atualizado que possui license CC-BY-4.0
    doc, _ = import_neuu_classic(baptist_json, memory_db)
    assert doc.id == doc_id
    assert doc.license == "CC-BY-4.0"

    # Valida no banco relacional se a licença persistida foi de fato atualizada
    cur = memory_db.execute("SELECT license FROM theological_documents WHERE id = ?", (doc_id,))
    assert cur.fetchone()[0] == "CC-BY-4.0"


def test_search_theological_returns_accurate_chapter_and_paragraph_numbers(memory_db):
    """Garante que o resultado FTS5 recupera o chapter_num e paragraph_num reais do texto."""
    root = Path(__file__).resolve().parent.parent
    baptist_json = root / "corpus" / "approved" / "theology" / "baptist-confession-1689.json"
    import_neuu_classic(baptist_json, memory_db)

    # Busca termo específico do Capítulo 4 ("ordenança")
    res = search_theological(memory_db, "Batismo ordenança")
    assert len(res) > 0
    top = res[0]
    # O resultado deve refletir o Capítulo 4 e o parágrafo real retornado pelo bm25
    assert top.chapter_num == 4
    assert top.paragraph_num in (2, 3)
    assert "Da Igreja e dos Sacramentos" in top.chapter_title
    assert f"§{top.paragraph_num}" in top.citation


