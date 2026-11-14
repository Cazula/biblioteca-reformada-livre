"""Interface de Linha de Comando (CLI) da Biblioteca Reformada Livre."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from biblioteca_reformada import __version__
from biblioteca_reformada.db import init_db, get_connection, get_db_path, reindex_fts, get_stats
from biblioteca_reformada.importer import import_approved_corpus, parse_blivre_raw_text
from biblioteca_reformada.licenses import audit_corpus
from biblioteca_reformada.search import execute_search, format_search_results


def find_project_root() -> Path:
    """Retorna o diretório raiz do projeto."""
    current = Path(__file__).resolve().parent
    while current.parent != current:
        if (current / "catalog" / "sources.json").exists() or (current / "pyproject.toml").exists():
            return current
        current = current.parent
    return Path.cwd()


def cmd_audit(args: argparse.Namespace) -> int:
    """Executa auditoria de licenças e validação de hashes SHA-256."""
    root = find_project_root()
    corpus_dir = root / "corpus" / "approved"
    catalog_file = root / "catalog" / "sources.json"

    print("=" * 80)
    print(f"AUDITORIA DE LICENÇAS E PROVENIÊNCIA — BIBLIOTECA REFORMADA LIVRE v{__version__}")
    print("=" * 80)
    print(f"Diretório do Corpus: {corpus_dir}")
    print(f"Catálogo de Fontes:  {catalog_file}")
    print("-" * 80)

    report = audit_corpus(corpus_dir, catalog_path=catalog_file)

    for item in report.file_results:
        status_tag = "[OK]  " if item.passed else "[FALHA]"
        print(f"{status_tag} {item.path}")
        print(f"       Licença: {item.license} (Permitida: {item.is_license_allowed})")
        print(f"       SHA-256 Esperado: {item.sha256_expected}")
        print(f"       SHA-256 Real:     {item.sha256_actual}")
        if item.error:
            print(f"       Erro: {item.error}")
        print()

    print("-" * 80)
    print(f"Total de arquivos auditados: {report.total_files}")
    print(f"Arquivos aprovados:          {report.passed_files}")
    print(f"Arquivos com divergência:    {report.failed_files}")
    print(f"Fontes no catálogo global:   {report.catalog_sources_count}")
    print(f"Fontes aprovadas no catálogo:{report.catalog_approved_count}")
    print(f"Fontes retidas em quarentena:{report.catalog_quarantine_count}")
    print("=" * 80)

    if report.all_passed:
        print("[SUCESSO] Todos os arquivos do corpus foram verificados e auditados com êxito!")
        return 0
    else:
        print("[ERRO] Auditoria reprovada: foram detectadas inconsistências no corpus.")
        return 1


def cmd_sync(args: argparse.Namespace) -> int:
    """Executa sincronização ou simulação (dry-run) de clonagem das fontes upstream."""
    root = find_project_root()
    catalog_file = root / "catalog" / "sources.json"
    sources_dir = root / "data" / "sources"

    if not catalog_file.exists():
        print(f"[ERRO] Arquivo de catálogo não encontrado: {catalog_file}")
        return 1

    with open(catalog_file, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    sources = catalog.get("sources", [])
    if args.source:
        sources = [s for s in sources if s.get("id") == args.source]

    print("=" * 80)
    mode_label = "EXECUÇÃO DE CLONAGEM (--fetch)" if args.fetch else "SIMULAÇÃO (DRY-RUN)"
    print(f"SINCRONIZAÇÃO DE FONTES UPSTREAM — {mode_label}")
    print(f"Destino local (ignorado no Git): {sources_dir}")
    print("=" * 80)

    sources_dir.mkdir(parents=True, exist_ok=True)
    success_count = 0
    fail_count = 0
    skipped_count = 0

    for s in sources:
        sid = s.get("id")
        name = s.get("name")
        repo_url = s.get("repo_url")
        status = s.get("status")
        license_decl = s.get("declared_license")

        print(f"\n[Fonte: {sid}] {name}")
        print(f"  URL:     {repo_url or 'N/A (Metadados institucionais)'}")
        print(f"  Licença: {license_decl} | Status: {status}")

        if not repo_url:
            print("  -> Ignorado para clone: fonte institucional sem repositório Git público.")
            skipped_count += 1
            continue

        target_path = sources_dir / sid
        if target_path.exists():
            print(f"  -> Já clonado em disco: {target_path}")
            skipped_count += 1
            continue

        if not args.fetch:
            print(f"  -> [DRY-RUN] Seria clonado via: git clone --depth 1 {repo_url} {target_path}")
            continue

        # Execução de clone seguro com profundidade 1 sem LFS pesado
        print(f"  -> Executando clone shallow (--depth 1)...")
        cmd = ["git", "clone", "--depth", "1", repo_url, str(target_path)]
        env = {**os.environ, "GIT_LFS_SKIP_SMUDGE": "1", "GIT_TERMINAL_PROMPT": "0"}
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env, stdin=subprocess.DEVNULL)
            if res.returncode == 0:
                print(f"  [OK] Clone concluído com sucesso em {target_path}")
                success_count += 1
            else:
                err_msg = res.stderr.strip() or res.stdout.strip()
                print(f"  [FALHA] Falha no clone (código {res.returncode}): {err_msg}")
                fail_count += 1
        except subprocess.TimeoutExpired:
            print(f"  [FALHA] Timeout de 120s atingido ao tentar clonar {repo_url}")
            fail_count += 1
        except Exception as ex:
            print(f"  [FALHA] Exceção ao clonar: {ex}")
            fail_count += 1

    print("\n" + "=" * 80)
    print(f"Resumo da Sincronização: {success_count} clonados, {skipped_count} ignorados/existentes, {fail_count} falhas.")
    print("=" * 80)
    return 0 if fail_count == 0 else 1


def cmd_import_blivre(args: argparse.Namespace) -> int:
    """Importa obras auditadas da Bíblia Livre para o banco SQLite."""
    root = find_project_root()
    corpus_approved_dir = root / "corpus" / "approved"
    db_path = get_db_path(args.db)

    print("=" * 80)
    print("INGESTÃO DA BÍBLIA LIVRE (BLIVRE) PARA SQLITE")
    print(f"Origem do Corpus Aprovado: {corpus_approved_dir}")
    print(f"Banco de Dados Destino:    {db_path}")
    print("=" * 80)

    conn = init_db(db_path)
    imported = import_approved_corpus(corpus_approved_dir, conn)
    print(f"[OK] Versículos importados do corpus aprovado: {imported}")

    # Verifica se há dados brutos em data/sources/blivre
    blivre_source = root / "data" / "sources" / "blivre"
    if blivre_source.exists():
        print(f"[INFO] Varrendo repositório upstream local em {blivre_source}...")
        # Varre arquivos .txt ou .tsv se disponíveis
        raw_imported = 0
        for txt_file in blivre_source.rglob("*.txt"):
            verses = parse_blivre_raw_text(txt_file)
            if verses:
                raw_imported += len(verses)
                from biblioteca_reformada.db import insert_verses_batch
                insert_verses_batch(conn, verses)
        if raw_imported > 0:
            print(f"[OK] Versículos adicionais extraídos do upstream: {raw_imported}")

    # Reindexação FTS5 garantida
    indexed = reindex_fts(conn)
    print(f"[OK] Índice FTS5 atualizado com {indexed} versículos.")
    conn.close()
    return 0


def cmd_index(args: argparse.Namespace) -> int:
    """Reconstrói o índice de busca textual FTS5."""
    db_path = get_db_path(args.db)
    print(f"Reconstruindo índice FTS5 no banco de dados: {db_path}...")
    conn = init_db(db_path)
    count = reindex_fts(conn)
    conn.close()
    print(f"[OK] Índice FTS5 reconstruído com sucesso! Total de registros indexados: {count}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    """Executa consulta textual FTS5 e exibe citações exatas."""
    query = " ".join(args.query) if isinstance(args.query, list) else str(args.query)
    if not query.strip():
        print("[ERRO] Informe o termo de busca. Exemplo: bref search 'verdade'")
        return 1

    db_path = get_db_path(args.db)
    conn = init_db(db_path)
    results = execute_search(conn, query, limit=args.limit)
    output = format_search_results(query, results)
    print(output)
    conn.close()
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """Exibe estatísticas consolidadas do acervo e banco de dados."""
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
    print(f"Total de Versículos:   {stats.get('total_verses', 0)}")
    print(f"Livros Canônicos:      {stats.get('total_books', 0)}")
    print(f"Registros no FTS5:     {stats.get('fts_indexed_rows', 0)}")
    print(f"Documentos Teológicos: {stats.get('total_documents', 0)}")
    print(f"Fontes Catalogadas:    {cat_sources_count}")
    print("\nVersículos por Versão:")
    for ver, count in stats.get("verses_by_version", {}).items():
        print(f"  - {ver}: {count} versículos")
    print("=" * 80)
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
    p_sync.add_argument("--dry-run", action="store_true", default=False, help="Apenas simula a sincronização sem clonar.")
    p_sync.add_argument("--fetch", action="store_true", default=False, help="Executa a clonagem rasa real das fontes.")
    p_sync.add_argument("--source", type=str, default=None, help="Filtra por identificador de fonte específico.")
    p_sync.set_defaults(func=cmd_sync)

    # import-blivre
    p_imp = subparsers.add_parser("import-blivre", help="Importa o acervo auditado da Bíblia Livre para o SQLite.")
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

    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
