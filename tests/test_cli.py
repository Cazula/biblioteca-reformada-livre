"""Testes da interface de linha de comando (CLI)."""

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
