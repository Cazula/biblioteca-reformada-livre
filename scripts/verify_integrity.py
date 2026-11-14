#!/usr/bin/env python3
"""Script de verificação de integridade e conformidade de licenças."""

import sys
from pathlib import Path

# Adiciona src ao path para execução direta
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "src"))

from biblioteca_reformada.licenses import audit_corpus


def main():
    corpus_dir = root_dir / "corpus" / "approved"
    catalog_path = root_dir / "catalog" / "sources.json"
    print(f"[VERIFICAÇÃO] Auditando corpus em: {corpus_dir}")

    report = audit_corpus(corpus_dir, catalog_path=catalog_path)
    print(f"Total de arquivos: {report.total_files}")
    print(f"Aprovados: {report.passed_files}")
    print(f"Falhas: {report.failed_files}")

    for r in report.file_results:
        status = "OK" if r.passed else "FALHA"
        print(f"[{status}] {r.path} -> SHA256: {r.sha256_actual[:12]}... Licença: {r.license}")

    if report.all_passed:
        print("[SUCESSO] Integridade 100% verificada.")
        return 0
    else:
        print("[ERRO] Divergências encontradas.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
