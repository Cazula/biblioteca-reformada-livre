"""Auditoria rigorosa de licenças, integridade criptográfica (SHA-256) e proveniência."""

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple

HEX64_REGEX = re.compile(r"^[0-9a-fA-F]{64}$")


def is_valid_sha256(val: Any) -> bool:
    """Verifica se o valor é uma string estritamente composta por 64 dígitos hexadecimais."""
    return isinstance(val, str) and bool(HEX64_REGEX.match(val.strip()))


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
    unmanifested_files: int = 0
    file_results: List[FileAuditResult] = field(default_factory=list)
    catalog_sources_count: int = 0
    catalog_approved_count: int = 0
    catalog_quarantine_count: int = 0

    @property
    def all_passed(self) -> bool:
        return self.failed_files == 0 and self.unmanifested_files == 0 and self.total_files > 0


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
    """Executa auditoria completa do diretório corpus/approved com validação bidirecional."""
    corpus_root = corpus_dir.resolve()
    manifest_file = manifest_path.resolve() if manifest_path else (corpus_root / "manifest.json")
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

    manifested_paths: Set[str] = set()

    for entry in entries:
        rel_path = entry.get("path", "")
        expected_hash = entry.get("sha256", "")
        declared_license = entry.get("license", "")

        # Validação de confinamento e rejeição de caminhos maliciosos
        if not rel_path or os.path.isabs(rel_path) or ".." in Path(rel_path).parts:
            res = FileAuditResult(
                path=rel_path,
                sha256_expected=expected_hash,
                sha256_actual="",
                license=declared_license,
                is_license_allowed=False,
                is_hash_matching=False,
                exists=False,
                error="Caminho inválido ou tentativa de escape fora de corpus/approved"
            )
            report.failed_files += 1
            report.file_results.append(res)
            continue

        target_file = (corpus_root / rel_path).resolve()
        # Garante confinamento estrito dentro de corpus_root via is_relative_to
        if not target_file.is_relative_to(corpus_root) or target_file == corpus_root:
            res = FileAuditResult(
                path=rel_path,
                sha256_expected=expected_hash,
                sha256_actual="",
                license=declared_license,
                is_license_allowed=False,
                is_hash_matching=False,
                exists=False,
                error="Violação de confinamento: arquivo fora do diretório do corpus"
            )
            report.failed_files += 1
            report.file_results.append(res)
            continue

        # Normaliza caminho relativo para conferência inversa
        norm_rel = str(target_file.relative_to(corpus_root)).replace("\\", "/")
        manifested_paths.add(norm_rel)

        # Validação do formato do SHA-256 no manifesto
        if not is_valid_sha256(expected_hash):
            res = FileAuditResult(
                path=rel_path,
                sha256_expected=expected_hash,
                sha256_actual="",
                license=declared_license,
                is_license_allowed=False,
                is_hash_matching=False,
                exists=target_file.exists(),
                error="Entrada no manifesto com sha256 ausente, vazio ou formato inválido (deve ter 64 dígitos hex)"
            )
            report.failed_files += 1
            report.file_results.append(res)
            continue

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
                "Hash divergente" if not hash_ok else f"Licença '{declared_license}' não permitida para distribuição"
            )
        )

        if res.passed:
            report.passed_files += 1
        else:
            report.failed_files += 1

        report.file_results.append(res)

    # Verificação bidirecional: nenhum arquivo em corpus/approved pode existir sem estar no manifesto
    if corpus_root.exists():
        for disk_file in corpus_root.rglob("*"):
            if not disk_file.is_file():
                continue

            resolved_disk = disk_file.resolve()
            # Confinamento seguro contra links simbólicos externos
            if not resolved_disk.is_relative_to(corpus_root):
                report.unmanifested_files += 1
                report.failed_files += 1
                res = FileAuditResult(
                    path=disk_file.name,
                    sha256_expected="N/A",
                    sha256_actual="",
                    license="N/A",
                    is_license_allowed=False,
                    is_hash_matching=False,
                    exists=True,
                    error="Link externo ou escape fora do diretório do corpus detectado"
                )
                report.file_results.append(res)
                continue

            if resolved_disk == manifest_file:
                continue

            norm_disk_rel = str(resolved_disk.relative_to(corpus_root)).replace("\\", "/")
            if norm_disk_rel not in manifested_paths:
                report.unmanifested_files += 1
                report.failed_files += 1
                res = FileAuditResult(
                    path=norm_disk_rel,
                    sha256_expected="N/A",
                    sha256_actual=compute_sha256(resolved_disk),
                    license="N/A",
                    is_license_allowed=False,
                    is_hash_matching=False,
                    exists=True,
                    error="Arquivo não registrado no manifesto de proveniência (distribuição não autorizada)"
                )
                report.file_results.append(res)

    return report
