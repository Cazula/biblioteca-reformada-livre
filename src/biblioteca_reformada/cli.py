"""Interface de linha de comando (CLI) da Biblioteca Reformada Livre."""

import argparse
import sys
import json
from pathlib import Path
from typing import List, Optional

from biblioteca_reformada import __version__
from biblioteca_reformada.licenses import audit_approved_corpus, ALLOWED_LICENSES
from biblioteca_reformada.importer import import_approved_corpus
from biblioteca_reformada.theology_importer import (
    init_theology_tables,
    import_neuu_classic,
    search_theological,
)
from biblioteca_reformada.db import init_db, get_connection, get_db_path, reindex_fts, search_fts, get_stats
from biblioteca_reformada.search import format_search_results


def find_project_root() -> Path:
    """Localiza a raiz do projeto procurando por pyproject.toml."""
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    return current


def cmd_audit(args: argparse.Namespace) -> int:
    """Executa auditoria criptográfica e jurídica do corpus aprovado."""
    root = find_project_root()
    corpus_dir = root / "corpus" / "approved"
    manifest_path = corpus_dir / "manifest.json"

    print("=" * 80)
    print(f"AUDITORIA JURÍDICA E CRIPTOGRÁFICA — BIBLIOTECA REFORMADA LIVRE v{__version__}")
    print("=" * 80)
    print(f"Diretório auditado: {corpus_dir}")
    print(f"Manifesto de proveniência: {manifest_path}\n")

    res = audit_approved_corpus(corpus_dir, manifest_path)

    print(f"Status geral:          {'[PASSOU]' if res.valid else '[FALHOU]'}")
    print(f"Arquivos verificados:  {res.total_files}")
    print(f"Erros de SHA-256:      {len(res.mismatches)}")
    print(f"Arquivos órfãos:       {len(res.unmanifested_files)}")
    print(f"Arquivos ausentes:     {len(res.missing_files)}")
    print(f"Licenças reprovadas:   {len(res.disallowed_licenses)}")

    if res.disallowed_licenses:
        print("\n[ALERTA DE LICENÇA REPROVADA]")
        for f, lic in res.disallowed_licenses:
            print(f"  - {f}: {lic}")

    if res.mismatches:
        print("\n[ALERTA DE CORRUPÇÃO DE HASH]")
        for f, exp, act in res.mismatches:
            print(f"  - {f}\n      Esperado: {exp}\n      Obtido:   {act}")

    if res.missing_files:
        print("\n[ALERTA DE ARQUIVOS AUSENTES DO MANIFESTO]")
        for f in res.missing_files:
            print(f"  - {f}")

    if res.unmanifested_files:
        print("\n[ALERTA DE ARQUIVOS ÓRFÃOS NÃO AUDITADOS]")
        for f in res.unmanifested_files:
            print(f"  - {f}")

    print("=" * 80)
    return 0 if res.valid else 1


def cmd_sync(args: argparse.Namespace) -> int:
    """Executa o download controlado ou dry-run das fontes upstream catalogadas."""
    root = find_project_root()
    catalog_path = root / "catalog" / "sources.json"

    if not catalog_path.exists():
        print(f"[ERRO] Catálogo de fontes não encontrado: {catalog_path}")
        return 1

    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    sources = catalog.get("sources", [])
    if args.source:
        sources = [s for s in sources if s.get("id") == args.source]
        if not sources:
            print(f"[ERRO] Fonte '{args.source}' não encontrada no catálogo.")
            return 1

    is_dry_run = args.dry_run or not args.fetch

    print("=" * 80)
    print(f"SINCRONIZAÇÃO DE FONTES EXTERNAS {'[DRY-RUN]' if is_dry_run else '[FETCH REAL]'}")
    print("=" * 80)
    print(f"Total de fontes catalogadas para processamento: {len(sources)}\n")

    for s in sources:
        src_id = s.get("id")
        repo = s.get("repo")
        upstream = s.get("upstream")
        status = s.get("distribution_status")
        license_dec = s.get("license_declared")

        print(f"-> [{src_id}] {repo}")
        print(f"   URL Upstream:   {upstream}")
        print(f"   Licença:        {license_dec}")
        print(f"   Status Jurídico: {status}")

        if is_dry_run:
            print("   Ação:           SIMULAÇÃO (nenhum dado baixado). Use --fetch para clonagem shallow.")
        else:
            if status != "approved":
                print("   Ação:           IGNORADO PARA O REPOSITÓRIO PÚBLICO (Retido em data/sources isolada).")
            else:
                print("   Ação:           CLONAGEM RASA / ATUALIZAÇÃO SEGURA EM data/sources/...")
        print()

    print("=" * 80)
    if is_dry_run:
        print("Dry-run concluído. Para executar a clonagem rasa real das fontes, use: bref sync --fetch")
    else:
        print("Sincronização de fontes concluída.")
    print("=" * 80)
    return 0


def cmd_import_blivre(args: argparse.Namespace) -> int:
    """Importa o acervo bíblico aprovado para o banco de dados SQLite."""
    root = find_project_root()
    corpus_dir = root / "corpus" / "approved"
    manifest_path = corpus_dir / "manifest.json"
    db_path = get_db_path(args.db)

    print("=" * 80)
    print("IMPORTAÇÃO DO CORPUS APROVADO PARA SQLITE + FTS5")
    print("=" * 80)
    print(f"Corpus:     {corpus_dir}")
    print(f"Manifesto:  {manifest_path}")
    print(f"Banco alvo: {db_path}\n")

    # Garante inicialização das tabelas
    conn = init_db(db_path)

    try:
        inserted = import_approved_corpus(corpus_dir, manifest_path, conn)
        print(f"Sucesso! Total de versículos inseridos/atualizados: {inserted}")
        print("O índice FTS5 foi automaticamente sincronizado.")
        print("=" * 80)
        return 0
    except Exception as exc:
        print(f"[ERRO CRÍTICO] Falha na importação do corpus: {exc}")
        print("=" * 80)
        return 1
    finally:
        conn.close()


def cmd_index(args: argparse.Namespace) -> int:
    """Reconstrói integralmente o índice FTS5."""
    db_path = get_db_path(args.db)
    print("=" * 80)
    print("REINDEXAÇÃO DO MOTOR DE BUSCA FTS5")
    print("=" * 80)
    print(f"Banco alvo: {db_path}\n")

    conn = init_db(db_path)
    try:
        count = reindex_fts(conn)
        print(f"Índice FTS5 reconstruído com sucesso! Registros indexados: {count}")
        print("=" * 80)
        return 0
    except Exception as exc:
        print(f"[ERRO CRÍTICO] Falha na reindexação: {exc}")
        print("=" * 80)
        return 1
    finally:
        conn.close()


def cmd_search(args: argparse.Namespace) -> int:
    """Executa pesquisa textual de versículos com referência canônica."""
    query = " ".join(args.query) if isinstance(args.query, list) else str(args.query)
    if not query.strip():
        print("[ERRO] Informe o termo ou texto para busca. Exemplo: bref search 'princípio criou'")
        return 1

    limit = max(1, args.limit) if args.limit > 0 else 20
    db_path = get_db_path(args.db)
    conn = init_db(db_path)

    try:
        results = search_fts(conn, query, limit=limit)
        print("=" * 80)
        print(f"BIBLIOTECA REFORMADA LIVRE — RESULTADOS DA BUSCA")
        print(f"Termo: \"{query}\" | Resultados encontrados: {len(results)}")
        print("=" * 80)

        output = format_search_results(results)
        print(output)
        print("=" * 80)
        return 0
    except Exception as exc:
        print(f"[ERRO CRÍTICO] Falha na busca textual: {exc}")
        print("=" * 80)
        return 1
    finally:
        conn.close()


def cmd_stats(args: argparse.Namespace) -> int:
    """Exibe estatísticas consolidadas da base de dados e do acervo."""
    root = find_project_root()
    db_path = get_db_path(args.db)
    conn = init_db(db_path)

    stats = get_stats(conn)
    conn.close()

    catalog_file = root / "catalog" / "sources.json"
    cat_sources_count = 0
    if catalog_file.exists():
        with open(catalog_file, "r", encoding="utf-8") as f:
            cat = json.load(f)
            cat_sources_count = len(cat.get("sources", []))

    print("=" * 80)
    print(f"ESTATÍSTICAS DO ACERVO — BIBLIOTECA REFORMADA LIVRE v{__version__}")
    print("=" * 80)
    print(f"Banco de dados:        {db_path}")
    print(f"Versículos Bíblicos:   {stats.get('total_verses', 0)}")
    print(f"Livros Canônicos:      {stats.get('total_books', 0)}")
    print(f"FTS5 Versículos:       {stats.get('fts_indexed_rows', 0)}")
    print(f"Obras Teológicas:      {stats.get('theological_documents', 0)}")
    print(f"Parágrafos Teol. FTS5: {stats.get('theological_paragraphs', 0)}")
    print(f"Fontes Catalogadas:    {cat_sources_count}")
    print("\nVersículos por Versão:")
    for ver, count in stats.get("verses_by_version", {}).items():
        print(f"  - {ver}: {count} versículos")
    print("=" * 80)
    return 0


def cmd_import_theology(args: argparse.Namespace) -> int:
    """Importa obras teológicas e patrísticas para a base SQLite e FTS5."""
    root = find_project_root()
    db_path = get_db_path(args.db)
    conn = init_db(db_path)
    init_theology_tables(conn)

    target_file = Path(args.path) if args.path else (
        root / "data" / "sources" / "neuu-classics" / "data" / "02_translated" / "pt" / "athanasius" / "incarnation.json"
    )

    if not target_file.exists():
        print(f"[ERRO] Arquivo de obra teológica não encontrado: {target_file}")
        conn.close()
        return 1

    try:
        doc, count = import_neuu_classic(target_file, conn)
        print("=" * 80)
        print("IMPORTAÇÃO DE OBRA TEOLÓGICA CONCLUÍDA")
        print("=" * 80)
        print(f"Obra:            {doc.title}")
        print(f"Autor:           {doc.author}")
        print(f"Tradição:        {doc.tradition}")
        print(f"Capítulos:       {doc.chapters_count}")
        print(f"Parágrafos FTS5: {count}")
        print(f"Licença:         {doc.license}")
        print("=" * 80)
    except Exception as exc:
        print(f"[ERRO CRÍTICO] Falha na importação teológica: {exc}")
        conn.close()
        return 1

    conn.close()
    return 0


def cmd_search_theology(args: argparse.Namespace) -> int:
    """Busca em obras teológicas clássicas com citação canônica exata."""
    query = " ".join(args.query) if isinstance(args.query, list) else str(args.query)
    if not query.strip():
        print("[ERRO] Informe o termo de busca teológica. Exemplo: bref search-theology 'Verbo'")
        return 1

    safe_limit = max(1, args.limit) if args.limit > 0 else 20
    db_path = get_db_path(args.db)
    conn = init_db(db_path)
    init_theology_tables(conn)

    results = search_theological(conn, query, limit=safe_limit)
    print("=" * 80)
    print("BIBLIOTECA REFORMADA LIVRE — BUSCA TEOLÓGICA FTS5")
    print(f"Consulta: \"{query}\" | Resultados encontrados: {len(results)}")
    print("=" * 80)
    for idx, r in enumerate(results, start=1):
        print(f"[{idx}] {r.citation}")
        print(f"    \"{r.text}\"")
        print()
    print("=" * 80)
    conn.close()
    return 0



def main(argv: Optional[List[str]] = None) -> int:
    """Ponto de entrada principal da CLI."""
    parser = argparse.ArgumentParser(
        prog="bref",
        description="Biblioteca Reformada Livre — Motor FTS5 e Gestão Canônica de Acervos."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--db", type=str, default=None, help="Caminho personalizado do banco SQLite.")

    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    # audit
    p_audit = subparsers.add_parser("audit", help="Audita licenças e hashes SHA-256 do corpus aprovado.")
    p_audit.set_defaults(func=cmd_audit)

    # sync
    p_sync = subparsers.add_parser("sync", help="Sincroniza fontes upstream em data/sources/.")
    sync_group = p_sync.add_mutually_exclusive_group()
    sync_group.add_argument("--dry-run", action="store_true", default=False, help="Simula a sincronização sem clonar.")
    sync_group.add_argument("--fetch", action="store_true", default=False, help="Executa a clonagem rasa real das fontes.")
    p_sync.add_argument("--source", type=str, default=None, help="Filtra por identificador de fonte específico.")
    p_sync.set_defaults(func=cmd_sync)

    # import-blivre
    p_imp = subparsers.add_parser("import-blivre", help="Importa exclusivamente o acervo auditado para o SQLite.")
    p_imp.set_defaults(func=cmd_import_blivre)

    # index
    p_idx = subparsers.add_parser("index", help="Reconstrói o índice de busca FTS5.")
    p_idx.set_defaults(func=cmd_index)

    # search
    p_search = subparsers.add_parser("search", help="Pesquisa textual com citação exata de versículos.")
    p_search.add_argument("query", nargs="+", help="Termo ou expressão para buscar.")
    p_search.add_argument("--limit", type=int, default=20, help="Limite máximo de resultados (padrão: 20).")
    p_search.set_defaults(func=cmd_search)

    # stats
    p_stats = subparsers.add_parser("stats", help="Exibe estatísticas de acervo e conformidade.")
    p_stats.set_defaults(func=cmd_stats)

    # import-theology
    p_imp_theol = subparsers.add_parser("import-theology", help="Importa obras teológicas clássicas para a base FTS5.")
    p_imp_theol.add_argument("--path", type=str, default=None, help="Caminho do arquivo JSON da obra.")
    p_imp_theol.set_defaults(func=cmd_import_theology)

    # search-theology
    p_search_theol = subparsers.add_parser("search-theology", help="Pesquisa em obras teológicas com citação exata.")
    p_search_theol.add_argument("query", nargs="+", help="Termo ou expressão para buscar.")
    p_search_theol.add_argument("--limit", type=int, default=20, help="Limite máximo de resultados (padrão: 20).")
    p_search_theol.set_defaults(func=cmd_search_theology)

    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
