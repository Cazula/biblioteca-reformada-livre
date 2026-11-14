"""Módulo de importação e busca FTS5 de obras teológicas e patrísticas clássicas."""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from biblioteca_reformada.models import (
    TheologicalDocument,
    TheologicalParagraph,
    TheologicalSearchResult
)


def init_theology_tables(conn: sqlite3.Connection) -> None:
    """Cria tabelas relacionais e índice virtual FTS5 para literatura teológica."""
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS theological_documents (
                id TEXT PRIMARY KEY,
                work_id TEXT NOT NULL,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                tradition TEXT NOT NULL,
                category TEXT NOT NULL,
                language TEXT NOT NULL,
                license TEXT NOT NULL,
                attribution TEXT NOT NULL,
                chapters_count INTEGER DEFAULT 0,
                paragraphs_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS theological_paragraphs (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                work_id TEXT NOT NULL,
                chapter_num INTEGER NOT NULL,
                chapter_title TEXT,
                paragraph_num INTEGER NOT NULL,
                paragraph_id TEXT,
                text TEXT NOT NULL,
                language TEXT NOT NULL,
                citation TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES theological_documents(id)
            )
        """)

        conn.execute("CREATE INDEX IF NOT EXISTS idx_theol_para_doc ON theological_paragraphs(document_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_theol_para_work ON theological_paragraphs(work_id)")

        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS theological_fts USING fts5(
                document_id UNINDEXED,
                work_id UNINDEXED,
                author,
                title,
                chapter_title,
                citation UNINDEXED,
                text,
                tokenize = 'unicode61 remove_diacritics 2'
            )
        """)


def import_neuu_classic(
    file_path: Path,
    conn: sqlite3.Connection,
    tradition_override: Optional[str] = None
) -> Tuple[TheologicalDocument, int]:
    """Importa uma obra teológica do dataset NEUU Classics (formato JSON estruturado).
    
    Suporta tanto a versão traduzida para português (02_translated/pt/) quanto a versão em inglês (01_parsed/en/).
    Garante integridade transacional e indexação FTS5 automática.
    """
    target = file_path.resolve()
    if not target.exists() or not target.is_file():
        raise FileNotFoundError(f"Arquivo de obra clássica não encontrado: {target}")

    with open(target, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Estrutura inválida em {target}: raiz deve ser um objeto JSON.")

    meta = data.get("metadata", {})
    chapters_raw = data.get("chapters", [])

    canonical_id = meta.get("canonical_id") or target.stem
    title_pt = meta.get("title_pt") or meta.get("title") or target.stem
    title_en = meta.get("title_en") or meta.get("title") or ""
    author_pt = meta.get("author_pt") or meta.get("author_short") or meta.get("author_full") or "Autor Desconhecido"
    rights = meta.get("rights", "Public Domain")
    lang_translated = meta.get("lang_translated") or meta.get("language") or "pt"
    subjects = meta.get("subjects", [])
    category = subjects[0] if subjects else "Teologia Histórica"

    tradition = tradition_override or meta.get("tradition") or ("Patrística" if "athanasius" in canonical_id or "Early Church" in subjects else "Clássica Cristã")
    doc_id = f"{canonical_id}:{lang_translated}"
    if meta.get("license"):
        doc_license = meta.get("license")
    elif "neuu" in str(target).lower() or any(k in canonical_id for k in ("athanasius", "anselm", "kempis", "lawrence")):
        doc_license = "CC-BY-4.0"
    else:
        doc_license = meta.get("rights", "Public Domain")
    attribution = meta.get("source_edition") or meta.get("attribution") or f"NEUU Classics / CCEL (Domínio Público) — Licença editorial: CC BY 4.0 ({meta.get('translation_method', 'Editorial')})"

    paragraphs: List[TheologicalParagraph] = []
    valid_chapters = 0

    for ch_idx, ch in enumerate(chapters_raw, start=1):
        ch_num = ch.get("number", ch_idx)
        ch_title_pt = ch.get("title_pt") or ch.get("title") or f"Capítulo {ch_num}"
        subtitle = ch.get("subtitle_en") or ch.get("subtitle") or ""
        if subtitle and subtitle not in ch_title_pt:
            full_ch_title = f"{ch_title_pt}: {subtitle}" if ch_title_pt else subtitle
        else:
            full_ch_title = ch_title_pt

        # Dois formatos possíveis de parágrafo no NEUU dataset:
        # Formato A: text_pt em bloco único
        # Formato B: lista de paragraphs: [{"id": ..., "text": ...}]
        raw_paras = ch.get("paragraphs", [])
        text_block = ch.get("text_pt") or ch.get("text_en") or ch.get("text")

        if raw_paras:
            valid_chapters += 1
            for p_idx, p in enumerate(raw_paras, start=1):
                p_text = p.get("text", "").strip()
                if not p_text:
                    continue
                p_id = p.get("id") or f"p{p_idx}"
                citation = f"{author_pt}, {title_pt}, {full_ch_title}, §{p_idx}"
                paragraphs.append(TheologicalParagraph(
                    id=f"{doc_id}:ch{ch_num}:p{p_idx}",
                    document_id=doc_id,
                    work_id=canonical_id,
                    chapter_num=ch_num,
                    chapter_title=full_ch_title,
                    paragraph_num=p_idx,
                    paragraph_id=p_id,
                    text=p_text,
                    language=lang_translated,
                    citation=citation
                ))
        elif text_block:
            valid_chapters += 1
            # Quebra o bloco de texto por parágrafos duplos
            sub_paragraphs = [seg.strip() for seg in text_block.split("\n\n") if seg.strip()]
            for p_idx, p_text in enumerate(sub_paragraphs, start=1):
                citation = f"{author_pt}, {title_pt}, {full_ch_title}, §{p_idx}"
                paragraphs.append(TheologicalParagraph(
                    id=f"{doc_id}:ch{ch_num}:p{p_idx}",
                    document_id=doc_id,
                    work_id=canonical_id,
                    chapter_num=ch_num,
                    chapter_title=full_ch_title,
                    paragraph_num=p_idx,
                    paragraph_id=f"p{p_idx}",
                    text=p_text,
                    language=lang_translated,
                    citation=citation
                ))

    doc = TheologicalDocument(
        id=doc_id,
        work_id=canonical_id,
        title=title_pt,
        author=author_pt,
        tradition=tradition,
        category=category,
        language=lang_translated,
        license=doc_license,
        attribution=attribution,
        chapters_count=valid_chapters,
        paragraphs_count=len(paragraphs)
    )

    init_theology_tables(conn)

    with conn:
        # Gravação atômica do documento
        conn.execute("""
            INSERT INTO theological_documents (
                id, work_id, title, author, tradition, category, language,
                license, attribution, chapters_count, paragraphs_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                author = excluded.author,
                tradition = excluded.tradition,
                category = excluded.category,
                attribution = excluded.attribution,
                chapters_count = excluded.chapters_count,
                paragraphs_count = excluded.paragraphs_count
        """, (
            doc.id, doc.work_id, doc.title, doc.author, doc.tradition,
            doc.category, doc.language, doc.license, doc.attribution,
            doc.chapters_count, doc.paragraphs_count
        ))

        # Remove parágrafos antigos do documento para evitar duplicatas em reimportações
        conn.execute("DELETE FROM theological_paragraphs WHERE document_id = ?", (doc.id,))
        conn.execute("DELETE FROM theological_fts WHERE document_id = ?", (doc.id,))

        # Insere parágrafos relacionais e no índice FTS5
        for p in paragraphs:
            conn.execute("""
                INSERT INTO theological_paragraphs (
                    id, document_id, work_id, chapter_num, chapter_title,
                    paragraph_num, paragraph_id, text, language, citation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                p.id, p.document_id, p.work_id, p.chapter_num, p.chapter_title,
                p.paragraph_num, p.paragraph_id, p.text, p.language, p.citation
            ))

            conn.execute("""
                INSERT INTO theological_fts (
                    document_id, work_id, author, title, chapter_title, citation, text
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                p.document_id, p.work_id, doc.author, doc.title,
                p.chapter_title, p.citation, p.text
            ))

    return doc, len(paragraphs)


def search_theological(
    conn: sqlite3.Connection,
    query: str,
    limit: int = 20,
    offset: int = 0
) -> List[TheologicalSearchResult]:
    """Busca textual FTS5 em documentos teológicos com ranking bm25 e escape defensivo."""
    clean_query = query.strip()
    if not clean_query:
        return []

    safe_limit = max(1, limit) if limit > 0 else 20
    safe_offset = max(0, offset)

    terms = clean_query.split()
    if len(terms) == 1 and not any(c in clean_query for c in ('"', '*', 'NEAR', 'AND', 'OR', 'NOT')):
        safe_term = clean_query.replace('"', '""')
        fts_query = f'"{safe_term}"*'
    elif all(not any(c in t for c in ('"', '*', 'NEAR', 'AND', 'OR', 'NOT')) for t in terms):
        clean_terms = [t.replace('"', '""') for t in terms]
        fts_query = " ".join([f'"{ct}"' for ct in clean_terms])
    else:
        fts_query = clean_query

    try:
        cursor = conn.execute("""
            SELECT document_id, work_id, author, title, chapter_title, citation, text, bm25(theological_fts) as rank
            FROM theological_fts
            WHERE theological_fts MATCH ?
            ORDER BY rank
            LIMIT ? OFFSET ?
        """, (fts_query, safe_limit, safe_offset))
        rows = cursor.fetchall()
    except sqlite3.OperationalError as op_err:
        err_msg = str(op_err).lower()
        if any(kw in err_msg for kw in ("syntax error", "fts5:", "malformed", "parse error", "match", "unterminated")):
            escaped_literal = clean_query.replace('"', '""')
            cursor = conn.execute("""
                SELECT document_id, work_id, author, title, chapter_title, citation, text, bm25(theological_fts) as rank
                FROM theological_fts
                WHERE theological_fts MATCH ?
                ORDER BY rank
                LIMIT ? OFFSET ?
            """, (f'"{escaped_literal}"', safe_limit, safe_offset))
            rows = cursor.fetchall()
        else:
            raise

    results = []
    for row in rows:
        results.append(TheologicalSearchResult(
            document_id=row["document_id"],
            work_id=row["work_id"],
            author=row["author"],
            title=row["title"],
            chapter_num=1,
            chapter_title=row["chapter_title"] or "",
            paragraph_num=1,
            citation=row["citation"],
            text=row["text"],
            rank=float(row["rank"])
        ))
    return results

