"""Auditoria rigorosa de licenças, integridade criptográfica (SHA-256) e proveniência."""

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


ALLOWED_DISTRIBUTION_LICENSES = {
    "CC0-1.0",
    "Public Domain",
    "CC-BY-3.0-BR",
    "CC-BY-4.0",
    "MIT",
    "Apache-2.0"
}


@dataclass
class FileAuditResult:
    path: str
    sha256_expected: str
    sha256_actual: str
    license: str
    is_license_allowed: bool
    is_hash_matching: bool
    exists: bool
    error: Optional[str] = None

    @property
    def passed(self) -> bool:
        return self.exists and self.is_hash_matching and self.is_license_allowed and (self.error is None)


@dataclass
class AuditReport:
    manifest_path: str
    total_files: int = 0
    passed_files: int = 0
    failed_files: int = 0
    file_results: List[FileAuditResult] = field(default_factory=list)
    catalog_sources_count: int = 0
    catalog_approved_count: int = 0
    catalog_quarantine_count: int = 0

    @property
    def all_passed(self) -> bool:
        return self.failed_files == 0 and self.total_files > 0


def compute_sha256(file_path: Path) -> str:
    """Calcula o hash SHA-256 de um arquivo de forma eficiente."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()


def load_manifest(manifest_path: Path) -> Dict[str, Any]:
    """Carrega o manifesto de corpus aprovado."""
    if not manifest_path.exists():
        return {"version": "1.0.0", "files": []}
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_manifest(manifest_path: Path, data: Dict[str, Any]) -> None:
    """Salva o manifesto formatado em JSON com indentação consistente."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def audit_corpus(corpus_dir: Path, manifest_path: Optional[Path] = None, catalog_path: Optional[Path] = None) -> AuditReport:
    """Executa auditoria completa do diretório corpus/approved."""
    manifest_file = manifest_path or (corpus_dir / "manifest.json")
    report = AuditReport(manifest_path=str(manifest_file))

    # Carrega fontes do catálogo se fornecido
    if catalog_path and catalog_path.exists():
        with open(catalog_path, "r", encoding="utf-8") as f:
            cat = json.load(f)
            sources = cat.get("sources", [])
            report.catalog_sources_count = len(sources)
            report.catalog_approved_count = sum(1 for s in sources if s.get("status") in ("approved", "approved-for-reference"))
            report.catalog_quarantine_count = sum(1 for s in sources if "quarantine" in s.get("status", "") or "local" in s.get("status", ""))

    manifest = load_manifest(manifest_file)
    entries = manifest.get("files", [])
    report.total_files = len(entries)

    for entry in entries:
        rel_path = entry.get("path")
        expected_hash = entry.get("sha256", "")
        declared_license = entry.get("license", "")

        target_file = corpus_dir / rel_path
        if not target_file.exists():
            res = FileAuditResult(
                path=rel_path,
                sha256_expected=expected_hash,
                sha256_actual="",
                license=declared_license,
                is_license_allowed=declared_license in ALLOWED_DISTRIBUTION_LICENSES,
                is_hash_matching=False,
                exists=False,
                error="Arquivo não encontrado em disco"
            )
            report.failed_files += 1
            report.file_results.append(res)
            continue

        actual_hash = compute_sha256(target_file)
        hash_ok = (actual_hash.lower() == expected_hash.lower())
        license_ok = (declared_license in ALLOWED_DISTRIBUTION_LICENSES)

        res = FileAuditResult(
            path=rel_path,
            sha256_expected=expected_hash,
            sha256_actual=actual_hash,
            license=declared_license,
            is_license_allowed=license_ok,
            is_hash_matching=hash_ok,
            exists=True,
            error=None if (hash_ok and license_ok) else (
                "Hash divergente" if not hash_ok else "Licença não permitida para distribuição"
            )
        )

        if res.passed:
            report.passed_files += 1
        else:
            report.failed_files += 1

        report.file_results.append(res)

    return report
