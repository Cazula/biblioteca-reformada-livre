#!/usr/bin/env python3
"""Script de clonagem rasa e segura de fontes upstream catalogadas."""

import os
import subprocess
import sys
import shutil
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
data_sources = root_dir / "data" / "sources"

SOURCES = [
    ("blivre", "https://github.com/blivre/BibliaLivre.git"),
    ("euaggelion-biblia-publica", "https://github.com/Projeto-Euaggelion/biblia.publica.git"),
    ("biblia-conectada", "https://github.com/alexpiraginet-bot/biblia-conectada.git"),
    ("biblia-libera", "https://github.com/biblialibera/biblialibera.git"),
    ("neuu-classics", "https://github.com/neuu-org/bible-classics-dataset.git"),
    ("neuu-topics", "https://github.com/neuu-org/bible-topics-dataset.git"),
    ("neuu-crossrefs", "https://github.com/neuu-org/bible-crossrefs-dataset.git"),
    ("neuu-gazetteers", "https://github.com/neuu-org/bible-gazetteers-dataset.git"),
    ("neuu-dictionary", "https://github.com/neuu-org/bible-dictionary-dataset.git"),
    ("scriptorium-divinum", "https://github.com/rilsonjoas/scriptorium-divinum.git"),
    ("abel-santos", "https://github.com/separovichabel/abel-santos.git"),
    ("exegese360", "https://github.com/mpraes/exegese360.git"),
    ("cfw", "https://github.com/rickserrat/cfw.git"),
]


def get_dir_size_mb(path: Path) -> float:
    total = 0
    if not path.exists():
        return 0.0
    for p in path.rglob("*"):
        if p.is_file():
            try:
                total += p.stat().st_size
            except OSError:
                pass
    return round(total / (1024 * 1024), 2)


def clone_source(source_id: str, repo_url: str) -> dict:
    target = data_sources / source_id
    if target.exists():
        size_mb = get_dir_size_mb(target)
        return {
            "id": source_id,
            "url": repo_url,
            "status": "already_exists",
            "size_mb": size_mb,
            "message": f"Diretório existente ({size_mb} MB)"
        }

    env = {**dict(sys.modules['os'].environ), "GIT_LFS_SKIP_SMUDGE": "1", "GIT_TERMINAL_PROMPT": "0"}
    cmd = ["git", "clone", "--depth", "1", repo_url, str(target)]
    print(f"\n[CLONANDO] {source_id} de {repo_url}...")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env, stdin=subprocess.DEVNULL)
        if res.returncode == 0:
            size_mb = get_dir_size_mb(target)
            print(f"  [OK] Sucesso: {size_mb} MB")
            return {
                "id": source_id,
                "url": repo_url,
                "status": "cloned",
                "size_mb": size_mb,
                "message": "Clonado com sucesso"
            }
        else:
            err = res.stderr.strip() or res.stdout.strip()
            print(f"  [FALHA] Código {res.returncode}: {err[:150]}")
            return {
                "id": source_id,
                "url": repo_url,
                "status": "error",
                "size_mb": 0.0,
                "message": err[:200]
            }
    except subprocess.TimeoutExpired:
        print(f"  [FALHA] Timeout de 120s")
        return {
            "id": source_id,
            "url": repo_url,
            "status": "timeout",
            "size_mb": 0.0,
            "message": "Timeout de 120 segundos excedido"
        }
    except Exception as e:
        print(f"  [FALHA] Exceção: {e}")
        return {
            "id": source_id,
            "url": repo_url,
            "status": "exception",
            "size_mb": 0.0,
            "message": str(e)
        }


def main():
    data_sources.mkdir(parents=True, exist_ok=True)
    results = []

    print("=" * 80)
    print("CLONAGEM RASA DE FONTES UPSTREAM — BIBLIOTECA REFORMADA LIVRE")
    print(f"Destino local (ignorado pelo Git): {data_sources}")
    print("=" * 80)

    for sid, url in SOURCES:
        res = clone_source(sid, url)
        results.append(res)

    print("\n" + "=" * 80)
    print("RELATÓRIO CONSOLIDADO DE CLONAGEM:")
    print("=" * 80)
    total_mb = 0.0
    for r in results:
        status_tag = f"[{r['status'].upper()}]".ljust(18)
        print(f"{status_tag} {r['id'].ljust(26)}: {r['size_mb']} MB — {r['message']}")
        total_mb += r["size_mb"]

    print("-" * 80)
    print(f"Espaço total em disco das fontes clonadas: {round(total_mb, 2)} MB")
    print("=" * 80)


if __name__ == "__main__":
    main()
