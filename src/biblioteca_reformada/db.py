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


def insert_verses_batch(
    conn: sqlite3.Connection,
    verses: List[Verse],
    sync_fts: bool = True,
    in_transaction: bool = False
) -> int:
    """Insere ou atualiza em lote versículos com controle transacional e sincronização do FTS5."""
    if not verses:
        return 0

    inserted_or_updated = 0

    def _execute_inserts():
        nonlocal inserted_or_updated
        cursor = conn.cursor()
        for v in verses:
            cursor.execute("""
                INSERT INTO verses (book, chapter, verse, text, version_id, testament)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(book, chapter, verse, version_id)
                DO UPDATE SET text = excluded.text, testament = excluded.testament
            """, (v.book, v.chapter, v.verse, v.text, v.version_id, v.testament))
            inserted_or_updated += 1

        if sync_fts:
            reindex_fts(conn, in_transaction=True)

    if in_transaction:
        _execute_inserts()
    else:
        with conn:
            _execute_inserts()

    return inserted_or_updated


def reindex_fts(conn: sqlite3.Connection, in_transaction: bool = False) -> int:
    """Reconstrói completamente o índice FTS5 a partir da tabela relacional."""
    def _execute_reindex():
        conn.execute("DELETE FROM verses_fts")
        cursor = conn.execute("""
            INSERT INTO verses_fts (book, chapter, verse, text, version_id)
            SELECT book, CAST(chapter AS TEXT), CAST(verse AS TEXT), text, version_id
            FROM verses
        """)
        return cursor.rowcount

    if in_transaction:
        return _execute_reindex()
    else:
        with conn:
            return _execute_reindex()


def _escape_fts_token(token: str) -> str:
    """Escapa aspas duplas internas de um token para sintaxe FTS5."""
    clean = token.replace('"', '""')
    return f'"{clean}"'


def search_fts(conn: sqlite3.Connection, query: str, limit: int = 20, offset: int = 0) -> List[SearchResult]:
    """Executa busca textual FTS5 com sanitização, escape de aspas e ranking bm25."""
    clean_query = query.strip()
    if not clean_query:
        return []

    # Validação de limites
    safe_limit = max(1, limit) if limit > 0 else 20
    safe_offset = max(0, offset)

    # Sanitiza a query para syntax FTS5
    terms = clean_query.split()
    if len(terms) == 1 and not any(c in clean_query for c in ('"', '*', 'NEAR', 'AND', 'OR', 'NOT')):
        # Busca por prefixo se termo único sem operadores
        safe_term = clean_query.replace('"', '""')
        fts_query = f'"{safe_term}"*'
    elif all(not any(c in t for c in ('"', '*', 'NEAR', 'AND', 'OR', 'NOT')) for t in terms):
        # Múltiplos termos simples: envolve cada palavra em aspas escapadas
        fts_query = " ".join([_escape_fts_token(t) for t in terms])
    else:
        fts_query = clean_query

    try:
        cursor = conn.execute("""
            SELECT book, chapter, verse, text, version_id, bm25(verses_fts) as rank
            FROM verses_fts
            WHERE verses_fts MATCH ?
            ORDER BY rank
            LIMIT ? OFFSET ?
        """, (fts_query, safe_limit, safe_offset))
        rows = cursor.fetchall()
    except sqlite3.OperationalError as op_err:
        err_msg = str(op_err).lower()
        # Restringe o fallback defensivo estritamente a falhas de sintaxe e parser da query FTS5
        if any(kw in err_msg for kw in ("syntax error", "fts5:", "malformed", "parse error", "match", "unterminated")):
            escaped_literal = clean_query.replace('"', '""')
            try:
                cursor = conn.execute("""
                    SELECT book, chapter, verse, text, version_id, bm25(verses_fts) as rank
                    FROM verses_fts
                    WHERE verses_fts MATCH ?
                    ORDER BY rank
                    LIMIT ? OFFSET ?
                """, (f'"{escaped_literal}"', safe_limit, safe_offset))
                rows = cursor.fetchall()
            except sqlite3.OperationalError:
                return []
        else:
            # Propaga erros reais como tabela inexistente ('no such table'), corrupção ou indisponibilidade
            raise

    results = []
    for row in rows:
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

    try:
        cur = conn.execute("SELECT COUNT(*) FROM theological_documents")
        stats["theological_documents"] = cur.fetchone()[0]
        cur = conn.execute("SELECT COUNT(*) FROM theological_paragraphs")
        stats["theological_paragraphs"] = cur.fetchone()[0]
    except sqlite3.OperationalError:
        stats["theological_documents"] = 0
        stats["theological_paragraphs"] = 0

    cur = conn.execute("SELECT COUNT(*) FROM verses_fts")
    stats["fts_indexed_rows"] = cur.fetchone()[0]

    return stats
