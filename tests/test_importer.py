"""Testes do módulo de importação de livros canônicos e corpus."""

from pathlib import Path
import pytest

from biblioteca_reformada.importer import parse_book_json, import_approved_corpus
from biblioteca_reformada.db import init_db, get_stats


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
