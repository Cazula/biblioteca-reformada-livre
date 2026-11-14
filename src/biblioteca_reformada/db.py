"""Camada de persistência SQLite e motor FTS5 da Biblioteca Reformada Livre."""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from biblioteca_reformada.models import Verse, SearchResult


DEFAULT_DB_FILENAME = "biblioteca_reformada.sqlite3"


def get_db_path(custom_path: Optional[str] = None) -> Path:
    """Resolve o caminho do banco de dados SQLite."""
    if custom_path:
        return Path(custom_path).resolve()
    # Padrão: diretório raiz do projeto
    root_dir = Path(__file__).resolve().parent.parent.parent
    return root_dir / DEFAULT_DB_FILENAME


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Abre conexão SQLite com row_factory ativado."""
    path = db_path or get_db_path()
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Inicializa as tabelas relacionais e a tabela virtual FTS5."""
    conn = get_connection(db_path)
    with conn:
        # Tabela relacional de versículos
        conn.execute("""
            CREATE TABLE IF NOT EXISTS verses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book TEXT NOT NULL,
                chapter INTEGER NOT NULL,
                verse INTEGER NOT NULL,
                text TEXT NOT NULL,
                version_id TEXT NOT NULL,
                testament TEXT NOT NULL DEFAULT 'NT',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(book, chapter, verse, version_id)
            )
        """)

        # Índices relacionais
        conn.execute("CREATE INDEX IF NOT EXISTS idx_verses_lookup ON verses(book, chapter, verse)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_verses_version ON verses(version_id)")

        # Tabela FTS5 para busca textual ultraveloz
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS verses_fts USING fts5(
                book,
                chapter UNINDEXED,
                verse UNINDEXED,
                text,
                version_id,
                tokenize = 'unicode61 remove_diacritics 2'
            )
        """)

        # Tabela de documentos teológicos e confessionais
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                category TEXT NOT NULL,
                license TEXT NOT NULL,
                content TEXT NOT NULL,
                source_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Metadados do sistema
        conn.execute("""
            CREATE TABLE IF NOT EXISTS system_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            INSERT OR REPLACE INTO system_metadata (key, value)
            VALUES ('schema_version', '1.0.0')
        """)

    return conn


def insert_verses_batch(conn: sqlite3.Connection, verses: List[Verse]) -> int:
    """Insere em lote versículos na tabela relacional e no índice FTS5."""
    if not verses:
        return 0

    inserted_count = 0
    with conn:
        # Inserção relacional com IGNORE para duplicatas
        cursor = conn.cursor()
        for v in verses:
            cursor.execute("""
                INSERT OR IGNORE INTO verses (book, chapter, verse, text, version_id, testament)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (v.book, v.chapter, v.verse, v.text, v.version_id, v.testament))
            if cursor.rowcount > 0:
                inserted_count += 1
                # Inserção no FTS5
                conn.execute("""
                    INSERT INTO verses_fts (book, chapter, verse, text, version_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (v.book, str(v.chapter), str(v.verse), v.text, v.version_id))

    return inserted_count


def reindex_fts(conn: sqlite3.Connection) -> int:
    """Reconstrói completamente o índice FTS5 a partir da tabela relacional."""
    with conn:
        conn.execute("DELETE FROM verses_fts")
        cursor = conn.execute("""
            INSERT INTO verses_fts (book, chapter, verse, text, version_id)
            SELECT book, CAST(chapter AS TEXT), CAST(verse AS TEXT), text, version_id
            FROM verses
        """)
        return cursor.rowcount


def search_fts(conn: sqlite3.Connection, query: str, limit: int = 25, offset: int = 0) -> List[SearchResult]:
    """Executa busca textual FTS5 com suporte a ranking por relevância (bm25)."""
    # Trata termos vazios
    clean_query = query.strip()
    if not clean_query:
        return []

    # Sanitiza a query para syntax FTS5 se necessário
    # Se não contiver operadores lógicos ou aspas, faz busca por prefixo em cada palavra
    terms = clean_query.split()
    if len(terms) == 1 and not any(c in clean_query for c in ('"', '*', 'NEAR', 'AND', 'OR', 'NOT')):
        fts_query = f"{clean_query}*"
    elif all(not any(c in t for c in ('"', '*', 'NEAR', 'AND', 'OR', 'NOT')) for t in terms):
        fts_query = " ".join([f'"{t}"' for t in terms])
    else:
        fts_query = clean_query

    try:
        cursor = conn.execute("""
            SELECT book, chapter, verse, text, version_id, bm25(verses_fts) as rank
            FROM verses_fts
            WHERE verses_fts MATCH ?
            ORDER BY rank
            LIMIT ? OFFSET ?
        """, (fts_query, limit, offset))
    except sqlite3.OperationalError:
        # Fallback para busca literal com aspas em caso de sintaxe FTS5 inválida
        cursor = conn.execute("""
            SELECT book, chapter, verse, text, version_id, bm25(verses_fts) as rank
            FROM verses_fts
            WHERE verses_fts MATCH ?
            ORDER BY rank
            LIMIT ? OFFSET ?
        """, (f'"{clean_query}"', limit, offset))

    results = []
    for row in cursor.fetchall():
        results.append(SearchResult(
            book=row["book"],
            chapter=int(row["chapter"]),
            verse=int(row["verse"]),
            text=row["text"],
            version_id=row["version_id"],
            rank=float(row["rank"])
        ))
    return results


def get_stats(conn: sqlite3.Connection) -> Dict[str, Any]:
    """Coleta estatísticas consolidadas do banco de dados."""
    stats = {}

    cur = conn.execute("SELECT COUNT(*) FROM verses")
    stats["total_verses"] = cur.fetchone()[0]

    cur = conn.execute("SELECT COUNT(DISTINCT book) FROM verses")
    stats["total_books"] = cur.fetchone()[0]

    cur = conn.execute("SELECT DISTINCT version_id, COUNT(*) FROM verses GROUP BY version_id")
    stats["verses_by_version"] = {row[0]: row[1] for row in cur.fetchall()}

    cur = conn.execute("SELECT COUNT(*) FROM documents")
    stats["total_documents"] = cur.fetchone()[0]

    cur = conn.execute("SELECT COUNT(*) FROM verses_fts")
    stats["fts_indexed_rows"] = cur.fetchone()[0]

    return stats
