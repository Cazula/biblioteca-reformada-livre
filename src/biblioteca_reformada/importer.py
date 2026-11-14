"""Módulo de importação e normalização de textos bíblicos e acervos para SQLite."""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import sqlite3

from biblioteca_reformada.models import Verse, CANONICAL_BOOKS, BOOK_BY_NAME, BOOK_BY_ABBR
from biblioteca_reformada.db import insert_verses_batch


def parse_book_json(file_path: Path) -> List[Verse]:
    """Lê um arquivo JSON normalizado de livro bíblico e retorna lista de Verses."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    book_name = data.get("book", "")
    version_id = data.get("version", "BLIVRE")
    testament = data.get("testament", "NT")

    verses = []
    for chap in data.get("chapters", []):
        chap_num = chap.get("chapter", 1)
        for v in chap.get("verses", []):
            verses.append(Verse(
                book=book_name,
                chapter=chap_num,
                verse=v.get("verse", 1),
                text=v.get("text", "").strip(),
                version_id=version_id,
                testament=testament
            ))
    return verses


def import_approved_corpus(corpus_approved_dir: Path, conn: sqlite3.Connection) -> int:
    """Varre corpus/approved/ e importa todos os livros JSON para o banco SQLite."""
    total_imported = 0
    bible_dir = corpus_approved_dir / "bible"
    if not bible_dir.exists():
        return 0

    for json_file in bible_dir.rglob("*.json"):
        if json_file.name == "manifest.json":
            continue
        try:
            verses = parse_book_json(json_file)
            inserted = insert_verses_batch(conn, verses)
            total_imported += inserted
        except Exception as e:
            print(f"[AVISO] Falha ao importar {json_file}: {e}")

    return total_imported


def parse_blivre_raw_text(file_path: Path, version_id: str = "BLIVRE") -> List[Verse]:
    """Parseador genérico de linhas de texto do formato BLIVRE (ex: 'Livro C:V Texto' ou TSV)."""
    verses = []
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Tenta formatos usuais da BLivre (tab-separated: Book Abbr \t Chap \t Verse \t Text)
            parts = line.split("\t")
            if len(parts) >= 4:
                book_raw = parts[0].strip()
                try:
                    c = int(parts[1].strip())
                    v = int(parts[2].strip())
                    txt = parts[3].strip()
                    book_meta = BOOK_BY_ABBR.get(book_raw.lower()) or BOOK_BY_NAME.get(book_raw.lower())
                    book_name = book_meta["name"] if book_meta else book_raw
                    testament = book_meta["testament"] if book_meta else "NT"
                    verses.append(Verse(
                        book=book_name,
                        chapter=c,
                        verse=v,
                        text=txt,
                        version_id=version_id,
                        testament=testament
                    ))
                except ValueError:
                    continue
    return verses
