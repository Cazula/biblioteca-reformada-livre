"""Testes de integridade de licenças e hashes criptográficos SHA-256."""

import json
from pathlib import Path
import pytest

from biblioteca_reformada.licenses import (
    compute_sha256,
    audit_corpus,
    load_manifest,
    ALLOWED_DISTRIBUTION_LICENSES
)


def test_compute_sha256(tmp_path: Path):
    sample_file = tmp_path / "teste.txt"
    sample_file.write_text("Graça e Paz", encoding="utf-8")
    h1 = compute_sha256(sample_file)
    assert len(h1) == 64
    assert h1 == compute_sha256(sample_file)


def test_allowed_licenses_contains_cc_by():
    assert "CC-BY-3.0-BR" in ALLOWED_DISTRIBUTION_LICENSES
    assert "CC-BY-4.0" in ALLOWED_DISTRIBUTION_LICENSES
    assert "MIT" in ALLOWED_DISTRIBUTION_LICENSES
    assert "Public Domain" in ALLOWED_DISTRIBUTION_LICENSES
    # Licenças não permitidas para distribuição no corpus base
    assert "CC-BY-NC-ND-4.0" not in ALLOWED_DISTRIBUTION_LICENSES
    assert "All Rights Reserved" not in ALLOWED_DISTRIBUTION_LICENSES


def test_audit_approved_corpus():
    root = Path(__file__).resolve().parent.parent
    corpus_dir = root / "corpus" / "approved"
    catalog_path = root / "catalog" / "sources.json"

    report = audit_corpus(corpus_dir, catalog_path=catalog_path)
    assert report.total_files > 0
    assert report.failed_files == 0
    assert report.passed_files == report.total_files
    assert report.all_passed is True


def test_audit_detects_corrupted_hash(tmp_path: Path):
    # Cria corpus temporário com hash forjado
    c_dir = tmp_path / "approved"
    c_dir.mkdir()
    f = c_dir / "obra.json"
    f.write_text('{"conteudo": "original"}', encoding="utf-8")

    manifest = {
        "version": "1.0.0",
        "files": [
            {
                "path": "obra.json",
                "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
                "license": "CC-BY-3.0-BR"
            }
        ]
    }
    m_file = c_dir / "manifest.json"
    m_file.write_text(json.dumps(manifest), encoding="utf-8")

    rep = audit_corpus(c_dir, manifest_path=m_file)
    assert rep.failed_files == 1
    assert rep.all_passed is False
    assert "divergente" in rep.file_results[0].error.lower()
