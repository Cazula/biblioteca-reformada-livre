"""Testes do módulo de importação de livros canônicos e corpus com validação rigorosa."""

import json
import hashlib
from pathlib import Path
import pytest

from biblioteca_reformada.importer import parse_book_json, import_approved_corpus, CorpusImportError
from biblioteca_reformada.db import init_db, get_stats, insert_verses_batch
from biblioteca_reformada.models import Verse


def test_parse_book_json():
    root = Path(__file__).resolve().parent.parent
    sample_json = root / "corpus" / "approved" / "bible" / "blivre" / "64-3-joao.json"
    assert sample_json.exists()

    verses = parse_book_json(sample_json)
    assert len(verses) == 14
    v1 = verses[0]
    assert v1.book == "3 João"
    assert v1.chapter == 1
    assert v1.verse == 1
    assert "Gaio" in v1.text
    assert v1.version_id == "BLIVRE"
    assert v1.testament == "NT"

    v14 = verses[13]
    assert v14.verse == 14
    assert "Paz seja contigo" in v14.text


def test_parse_book_json_corrupted_hash(tmp_path: Path):
    f = tmp_path / "bad.json"
    f.write_text('{"book": "3 João", "version": "BLIVRE", "testament": "NT", "chapters": [{"chapter": 1, "verses": [{"verse": 1, "text": "X"}]}]}', encoding="utf-8")
    with pytest.raises(CorpusImportError) as exc_info:
        parse_book_json(f, expected_hash="0000000000000000000000000000000000000000000000000000000000000000")
    assert "adulterado" in str(exc_info.value).lower()


def test_parse_book_json_invalid_structure(tmp_path: Path):
    # Arquivo sem campo book
    f = tmp_path / "nobook.json"
    f.write_text('{"version": "BLIVRE", "testament": "NT", "chapters": []}', encoding="utf-8")
    with pytest.raises(CorpusImportError):
        parse_book_json(f)


def test_parse_book_json_unknown_book(tmp_path: Path):
    f = tmp_path / "unknown.json"
    f.write_text('{"book": "Evangelho Apócrifo Desconhecido", "version": "BLIVRE", "testament": "NT", "chapters": [{"chapter": 1, "verses": [{"verse": 1, "text": "Texto"}]}]}', encoding="utf-8")
    with pytest.raises(CorpusImportError) as exc_info:
        parse_book_json(f)
    assert "não reconhecido" in str(exc_info.value).lower()


def test_parse_book_json_incompatible_testament(tmp_path: Path):
    f = tmp_path / "bad_testament.json"
    # Gênesis deve ser AT, não NT
    f.write_text('{"book": "Gênesis", "version": "BLIVRE", "testament": "NT", "chapters": [{"chapter": 1, "verses": [{"verse": 1, "text": "No princípio"}]}]}', encoding="utf-8")
    with pytest.raises(CorpusImportError) as exc_info:
        parse_book_json(f)
    assert "incompatibilidade canônica" in str(exc_info.value).lower()


def test_parse_book_json_boolean_numbers_rejected(tmp_path: Path):
    # Booleano True não deve ser aceito como número de capítulo ou versículo
    f1 = tmp_path / "bool_chapter.json"
    f1.write_text('{"book": "3 João", "version": "BLIVRE", "testament": "NT", "chapters": [{"chapter": true, "verses": [{"verse": 1, "text": "Texto"}]}]}', encoding="utf-8")
    with pytest.raises(CorpusImportError) as exc_info1:
        parse_book_json(f1)
    assert "não booleano" in str(exc_info1.value).lower()

    f2 = tmp_path / "bool_verse.json"
    f2.write_text('{"book": "3 João", "version": "BLIVRE", "testament": "NT", "chapters": [{"chapter": 1, "verses": [{"verse": true, "text": "Texto"}]}]}', encoding="utf-8")
    with pytest.raises(CorpusImportError) as exc_info2:
        parse_book_json(f2)
    assert "não booleano" in str(exc_info2.value).lower()


def test_parse_book_json_duplicate_verse_rejected(tmp_path: Path):
    f = tmp_path / "dup.json"
    f.write_text('{"book": "3 João", "version": "BLIVRE", "testament": "NT", "chapters": [{"chapter": 1, "verses": [{"verse": 1, "text": "Verso A"}, {"verse": 1, "text": "Verso B"}]}]}', encoding="utf-8")
    with pytest.raises(CorpusImportError) as exc_info:
        parse_book_json(f)
    assert "duplicado" in str(exc_info.value).lower()


def test_import_approved_corpus():
    root = Path(__file__).resolve().parent.parent
    corpus_dir = root / "corpus" / "approved"

    conn = init_db(":memory:")
    imported = import_approved_corpus(corpus_dir, conn)
    assert imported >= 14

    stats = get_stats(conn)
    assert stats["total_verses"] >= 14
    assert "3 João" in [r[0] for r in conn.execute("SELECT DISTINCT book FROM verses").fetchall()]
    conn.close()


def test_import_approved_corpus_atomic_rollback(tmp_path: Path):
    """Verifica que se o 2º arquivo falhar, o 1º é revertido e verses/verses_fts ficam limpos."""
    c_dir = tmp_path / "approved"
    c_dir.mkdir()

    # Livro 1 válido
    b1 = c_dir / "livro1.json"
    b1_content = '{"book": "3 João", "version": "BLIVRE", "testament": "NT", "chapters": [{"chapter": 1, "verses": [{"verse": 1, "text": "Gaio amado"}]}]}'.encode("utf-8")
    b1.write_bytes(b1_content)
    h1 = hashlib.sha256(b1_content).hexdigest()

    # Livro 2 inválido (hash adulterado)
    b2 = c_dir / "livro2.json"
    b2_content = '{"book": "Judas", "version": "BLIVRE", "testament": "NT", "chapters": [{"chapter": 1, "verses": [{"verse": 1, "text": "Judas servo"}]}]}'.encode("utf-8")
    b2.write_bytes(b2_content)

    manifest = {
        "version": "1.0.0",
        "files": [
            {"path": "livro1.json", "sha256": h1, "license": "CC-BY-3.0-BR"},
            {"path": "livro2.json", "sha256": "0000000000000000000000000000000000000000000000000000000000000000", "license": "CC-BY-3.0-BR"}
        ]
    }
    m_file = c_dir / "manifest.json"
    m_file.write_text(json.dumps(manifest), encoding="utf-8")

    conn = init_db(":memory:")
    with pytest.raises(CorpusImportError):
        import_approved_corpus(c_dir, conn, manifest_path=m_file)

    # Atomicidade estrita: nenhum versículo foi gravado
    cur = conn.execute("SELECT COUNT(*) FROM verses")
    assert cur.fetchone()[0] == 0

    cur_fts = conn.execute("SELECT COUNT(*) FROM verses_fts")
    assert cur_fts.fetchone()[0] == 0
    conn.close()


def test_import_approved_corpus_rejects_empty_or_invalid_sha(tmp_path: Path):
    c_dir = tmp_path / "approved"
    c_dir.mkdir()
    b1 = c_dir / "livro1.json"
    b1.write_text('{"book": "3 João", "version": "BLIVRE", "testament": "NT", "chapters": [{"chapter": 1, "verses": [{"verse": 1, "text": "Gaio"}]}]}', encoding="utf-8")

    # Manifesto sem sha256 ou com sha256 vazio
    manifest = {
        "version": "1.0.0",
        "files": [
            {"path": "livro1.json", "sha256": "", "license": "CC-BY-3.0-BR"}
        ]
    }
    m_file = c_dir / "manifest.json"
    m_file.write_text(json.dumps(manifest), encoding="utf-8")

    conn = init_db(":memory:")
    with pytest.raises(CorpusImportError) as exc_info:
        import_approved_corpus(c_dir, conn, manifest_path=m_file)
    assert "sha256" in str(exc_info.value).lower()
    conn.close()


def test_import_approved_corpus_cross_file_duplicate_rejected(tmp_path: Path):
    c_dir = tmp_path / "approved"
    c_dir.mkdir()

    # Dois arquivos tentando inserir o mesmo versículo 3 João 1:1
    b1 = c_dir / "livro1.json"
    b1_content = '{"book": "3 João", "version": "BLIVRE", "testament": "NT", "chapters": [{"chapter": 1, "verses": [{"verse": 1, "text": "Texto A"}]}]}'.encode("utf-8")
    b1.write_bytes(b1_content)
    h1 = hashlib.sha256(b1_content).hexdigest()

    b2 = c_dir / "livro2.json"
    b2_content = '{"book": "3 João", "version": "BLIVRE", "testament": "NT", "chapters": [{"chapter": 1, "verses": [{"verse": 1, "text": "Texto B divergente"}]}]}'.encode("utf-8")
    b2.write_bytes(b2_content)
    h2 = hashlib.sha256(b2_content).hexdigest()

    manifest = {
        "version": "1.0.0",
        "files": [
            {"path": "livro1.json", "sha256": h1, "license": "CC-BY-3.0-BR"},
            {"path": "livro2.json", "sha256": h2, "license": "CC-BY-3.0-BR"}
        ]
    }
    m_file = c_dir / "manifest.json"
    m_file.write_text(json.dumps(manifest), encoding="utf-8")

    conn = init_db(":memory:")
    with pytest.raises(CorpusImportError) as exc_info:
        import_approved_corpus(c_dir, conn, manifest_path=m_file)
    assert "colisão/duplicação" in str(exc_info.value).lower()
    conn.close()
