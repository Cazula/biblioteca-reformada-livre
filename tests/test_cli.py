"""Testes da interface de linha de comando (CLI)."""

import json
from pathlib import Path
import pytest

from biblioteca_reformada.cli import main


def test_cli_help(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "bref" in captured.out
    assert "audit" in captured.out
    assert "search" in captured.out


def test_cli_no_args_shows_help(capsys):
    ret = main([])
    assert ret == 0
    captured = capsys.readouterr()
    assert "bref" in captured.out


def test_cli_audit():
    ret = main(["audit"])
    assert ret == 0


def test_cli_sync_dry_run(capsys):
    ret = main(["sync", "--dry-run"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "SIMULAÇÃO (DRY-RUN)" in captured.out
    assert "blivre" in captured.out


def test_cli_import_and_search(tmp_path: Path, capsys):
    test_db = tmp_path / "test_cli.sqlite3"

    # Importa
    ret_imp = main(["--db", str(test_db), "import-blivre"])
    assert ret_imp == 0

    # Indexa
    ret_idx = main(["--db", str(test_db), "index"])
    assert ret_idx == 0

    # Busca
    ret_search = main(["--db", str(test_db), "search", "verdade"])
    assert ret_search == 0
    captured = capsys.readouterr()
    assert "3 João" in captured.out
    assert "verdade" in captured.out

    # Estatísticas
    ret_stats = main(["--db", str(test_db), "stats"])
    assert ret_stats == 0


def test_cli_sync_rejects_unsafe_source_id(tmp_path: Path, monkeypatch, capsys):
    from biblioteca_reformada.cli import cmd_sync
    import argparse

    fake_root = tmp_path / "proj"
    fake_root.mkdir()
    cat_dir = fake_root / "catalog"
    cat_dir.mkdir()
    cat_file = cat_dir / "sources.json"

    # Catálogo contendo id malicioso com path traversal
    bad_catalog = {
        "sources": [
            {
                "id": "../../malicious_escape",
                "name": "Fonte Maliciosa",
                "repo_url": "https://github.com/exemplo/malicioso.git",
                "status": "quarantine",
                "declared_license": "MIT"
            }
        ]
    }
    cat_file.write_text(json.dumps(bad_catalog), encoding="utf-8")

    monkeypatch.setattr("biblioteca_reformada.cli.find_project_root", lambda: fake_root)

    args = argparse.Namespace(fetch=True, dry_run=False)
    ret = cmd_sync(args)
    # Deve falhar ou rejeitar a fonte
    assert ret == 1
    captured = capsys.readouterr()
    assert "REJEITADO" in captured.out


def test_cli_theology_import_and_search(tmp_path: Path, capsys):
    test_db = tmp_path / "test_theol_cli.sqlite3"
    root = Path(__file__).resolve().parent.parent
    athanasius_json = root / "data" / "sources" / "neuu-classics" / "data" / "02_translated" / "pt" / "athanasius" / "incarnation.json"

    if not athanasius_json.exists():
        pytest.skip("Dataset local de Atanásio não presente")

    ret_imp = main(["--db", str(test_db), "import-theology", "--path", str(athanasius_json)])
    assert ret_imp == 0
    captured_imp = capsys.readouterr()
    assert "Atanásio" in captured_imp.out

    ret_search = main(["--db", str(test_db), "search-theology", "Verbo"])
    assert ret_search == 0
    captured_search = capsys.readouterr()
    assert "Atanásio" in captured_search.out
    assert "Encarnação" in captured_search.out
