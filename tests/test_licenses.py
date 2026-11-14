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
    assert report.unmanifested_files == 0
    assert report.passed_files == report.total_files
    assert report.all_passed is True


def test_audit_detects_corrupted_hash(tmp_path: Path):
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


def test_audit_detects_unmanifested_orphan_file(tmp_path: Path):
    c_dir = tmp_path / "approved"
    c_dir.mkdir()
    f_ok = c_dir / "obra_ok.json"
    f_ok.write_text('{"ok": true}', encoding="utf-8")
    hash_ok = compute_sha256(f_ok)

    # Arquivo órfão não declarado
    f_orphan = c_dir / "intruso.json"
    f_orphan.write_text('{"intruso": true}', encoding="utf-8")

    manifest = {
        "version": "1.0.0",
        "files": [
            {
                "path": "obra_ok.json",
                "sha256": hash_ok,
                "license": "CC-BY-3.0-BR"
            }
        ]
    }
    m_file = c_dir / "manifest.json"
    m_file.write_text(json.dumps(manifest), encoding="utf-8")

    rep = audit_corpus(c_dir, manifest_path=m_file)
    assert rep.unmanifested_files == 1
    assert rep.failed_files == 1
    assert rep.all_passed is False


def test_audit_rejects_path_traversal_escape(tmp_path: Path):
    c_dir = tmp_path / "approved"
    c_dir.mkdir()
    manifest = {
        "version": "1.0.0",
        "files": [
            {
                "path": "../../outside.json",
                "sha256": "abc",
                "license": "CC-BY-3.0-BR"
            }
        ]
    }
    m_file = c_dir / "manifest.json"
    m_file.write_text(json.dumps(manifest), encoding="utf-8")

    rep = audit_corpus(c_dir, manifest_path=m_file)
    assert rep.failed_files == 1
    assert rep.all_passed is False
    assert "escape" in rep.file_results[0].error.lower() or "confinamento" in rep.file_results[0].error.lower()


def test_audit_rejects_empty_or_invalid_sha(tmp_path: Path):
    c_dir = tmp_path / "approved"
    c_dir.mkdir()
    f = c_dir / "obra.json"
    f.write_text('{"ok": true}', encoding="utf-8")

    manifest = {
        "version": "1.0.0",
        "files": [
            {
                "path": "obra.json",
                "sha256": "invalido",
                "license": "CC-BY-3.0-BR"
            }
        ]
    }
    m_file = c_dir / "manifest.json"
    m_file.write_text(json.dumps(manifest), encoding="utf-8")

    rep = audit_corpus(c_dir, manifest_path=m_file)
    assert rep.failed_files == 1
    assert rep.all_passed is False
    assert "sha256" in rep.file_results[0].error.lower()


def test_audit_rejects_sibling_prefix_traversal(tmp_path: Path):
    root = tmp_path / "root"
    root.mkdir()
    c_dir = root / "approved"
    c_dir.mkdir()
    sibling = root / "approved-extra"
    sibling.mkdir()
    f_extra = sibling / "extra.json"
    f_extra.write_text('{"extra": true}', encoding="utf-8")

    manifest = {
        "version": "1.0.0",
        "files": [
            {
                "path": "../approved-extra/extra.json",
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
