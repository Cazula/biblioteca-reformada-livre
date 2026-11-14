"""Módulo de critérios de promoção canônica (candidate -> approved) e governança editorial.

Garante que nenhuma obra teológica ou bíblica seja integrada ao corpus aprovado sem:
1. Licença de distribuição compatível com a política do projeto.
2. Proveniência e edição-fonte primária verificáveis.
3. Classificação editorial rigorosa de completude (full/excerpt/abridged) e tipo de texto (original/translation/paraphrase).
4. Verificação criptográfica de integridade de leitura única (SHA-256 de 64 caracteres hexadecimais contra manifesto imutável).
5. Confinamento estrito de caminho (apenas arquivos em corpus/approved auditados no manifesto).
6. Validação exaustiva de esquema: todos os capítulos e parágrafos verificados sem exceção.
7. Coerência estrita de metadados internos (licença, identidade, completude, tipo de texto).
"""

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set

from biblioteca_reformada.licenses import ALLOWED_DISTRIBUTION_LICENSES, is_valid_sha256


class TextCompleteness(str, Enum):
    FULL = "full"
    EXCERPT = "excerpt"
    ABRIDGED = "abridged"


class TextType(str, Enum):
    ORIGINAL = "original"
    TRANSLATION = "translation"
    PARAPHRASE = "paraphrase"


class PromotionStatus(str, Enum):
    APPROVED = "approved"                     # Obra integral local, validada e presente no corpus
    APPROVED_EXCERPT = "approved-excerpt"     # Extrato local, validado e presente no corpus
    APPROVED_ABRIDGED = "approved-abridged"   # Obra abreviada local, validada e presente no corpus
    CANDIDATE_ELIGIBLE = "candidate-eligible" # Obra remota/catálogo com metadados e licença válidos
    QUARANTINE = "quarantine"                 # Retida em quarentena (ex: licença restrita)
    REJECTED = "rejected"                     # Impedimentos de licença, proveniência ou integridade


@dataclass
class PromotionEvaluation:
    work_id: str
    status: PromotionStatus
    is_promotable: bool
    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata_snapshot: Dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.is_promotable and len(self.reasons) == 0


def load_manifest_hashes(manifest_path: Path) -> Dict[str, str]:
    """Carrega o dicionário {caminho_normalizado: sha256} de corpus/approved/manifest.json."""
    if not manifest_path.exists():
        return {}
    try:
        raw = manifest_path.read_bytes()
        data = json.loads(raw.decode("utf-8"))
        return {
            entry["path"].replace("\\", "/"): entry["sha256"].lower()
            for entry in data.get("files", [])
            if "path" in entry and "sha256" in entry
        }
    except Exception:
        return {}


def evaluate_candidate_work(
    work: Dict[str, Any],
    file_path: Optional[Path] = None,
    allow_excerpts: bool = True,
    expected_sha: Optional[str] = None,
    require_file_exists: bool = False,
    require_manifest_entry: bool = False,
    approved_corpus_root: Optional[Path] = None
) -> PromotionEvaluation:
    """Avalia formalmente se uma obra atende aos critérios rigorosos de promoção e integridade."""
    work_id = str(work.get("work_id") or work.get("id") or "desconhecido")
    reasons: List[str] = []
    warnings: List[str] = []

    # 1. Validação de Licença
    declared_license = work.get("license")
    if not isinstance(declared_license, str) or not declared_license.strip():
        reasons.append("Licença não declarada ou inválida (campo 'license' deve ser string não vazia).")
        declared_license_str = ""
    else:
        declared_license_str = declared_license.strip()
        if declared_license_str not in ALLOWED_DISTRIBUTION_LICENSES:
            reasons.append(
                f"Licença '{declared_license_str}' não permitida para distribuição pública. "
                f"Permitidas: {sorted(list(ALLOWED_DISTRIBUTION_LICENSES))}"
            )

    # 2. Validação de Proveniência e Edição-Fonte
    source_edition = work.get("source_edition")
    if not isinstance(source_edition, str) or len(source_edition.strip()) < 5:
        reasons.append("Edição-fonte primária ausente ou insuficiente no campo 'source_edition'.")
        source_edition_str = ""
    else:
        source_edition_str = source_edition.strip()

    provenance_url = work.get("provenance_url")
    if not isinstance(provenance_url, str) or not provenance_url.strip():
        reasons.append("URL de proveniência ausente ou inválida (campo 'provenance_url').")
        provenance_url_str = ""
    else:
        provenance_url_str = provenance_url.strip()
        if not (provenance_url_str.startswith("http://") or provenance_url_str.startswith("https://") or provenance_url_str.startswith("corpus/")):
            reasons.append(f"URL de proveniência com esquema inseguro ou inválido: '{provenance_url_str}'.")

    # 3. Validação de Completude e Tipo de Texto
    completeness_raw = work.get("completeness")
    if not isinstance(completeness_raw, str) or not completeness_raw.strip():
        reasons.append("Grau de completude não especificado ('completeness' deve ser 'full', 'excerpt' ou 'abridged').")
        completeness_str = ""
    else:
        completeness_str = completeness_raw.strip()
        if completeness_str not in [e.value for e in TextCompleteness]:
            reasons.append(f"Valor inválido para 'completeness': '{completeness_str}'.")
        elif completeness_str == TextCompleteness.EXCERPT.value and not allow_excerpts:
            reasons.append("Extratos não são permitidos para promoção integral nesta política.")
        elif completeness_str == TextCompleteness.ABRIDGED.value and not allow_excerpts:
            reasons.append("Obras abreviadas (abridged) não são permitidas para promoção integral nesta política.")

    text_type_raw = work.get("text_type")
    if not isinstance(text_type_raw, str) or not text_type_raw.strip():
        reasons.append("Tipo de texto não especificado ('text_type' deve ser 'original', 'translation' ou 'paraphrase').")
        text_type_str = ""
    else:
        text_type_str = text_type_raw.strip()
        if text_type_str not in [t.value for t in TextType]:
            reasons.append(f"Valor inválido para 'text_type': '{text_type_str}'.")

    # Regra anti-falsificação de Domínio Público
    if text_type_str in (TextType.PARAPHRASE.value, TextType.TRANSLATION.value):
        lang = str(work.get("language", "")).lower()
        if "pt" in lang and declared_license_str == "Public Domain":
            reasons.append(
                "Inconsistência de direitos: tradução/paráfrase moderna em português não herda "
                "automaticamente o Domínio Público da obra histórica original. Requer licença permissiva expressa (ex: CC-BY-4.0)."
            )

    # Verificação de revisão humana
    human_reviewed = work.get("human_reviewed")
    if human_reviewed is None:
        warnings.append("Status de revisão humana ('human_reviewed') não informado; presumido False.")
    elif human_reviewed is False:
        warnings.append("Obra com 'human_reviewed: false' — deve conter nota editorial explícita.")

    # 4. Validação de Arquivo e Integridade Criptográfica (Single-read)
    file_validated_successfully = False
    if file_path is not None:
        target = file_path.resolve()
        if not target.exists() or not target.is_file():
            reasons.append(f"Arquivo local declarado não encontrado: {target}")
        else:
            # Confinamento de diretório caso especificado
            if approved_corpus_root is not None:
                try:
                    target.relative_to(approved_corpus_root.resolve())
                except ValueError:
                    reasons.append(
                        f"Violação de confinamento: o arquivo {target} está fora do corpus aprovado "
                        f"({approved_corpus_root.resolve()})."
                    )

            try:
                # Leitura única dos bytes para evitar Time-of-check to time-of-use
                raw_bytes = target.read_bytes()
                actual_sha = hashlib.sha256(raw_bytes).hexdigest().lower()

                # Verificação estrita de hash SHA-256
                if require_manifest_entry and not expected_sha:
                    reasons.append("Arquivo em corpus/approved não registrado no manifesto imutável manifest.json.")
                else:
                    effective_expected_sha = expected_sha or (work.get("sha256") if not require_manifest_entry else None)
                    if effective_expected_sha is None:
                        reasons.append("Hash SHA-256 esperado é obrigatório para validação de integridade do arquivo local.")
                    elif not isinstance(effective_expected_sha, str) or not is_valid_sha256(effective_expected_sha):
                        reasons.append(f"Hash SHA-256 esperado ausente, inválido ou malformado: '{effective_expected_sha}'.")
                    elif actual_sha != effective_expected_sha.lower():
                        reasons.append(f"Divergência de hash SHA-256: esperado {effective_expected_sha.lower()}, obtido {actual_sha}.")

                # Parse JSON a partir dos mesmos bytes lidos
                content = json.loads(raw_bytes.decode("utf-8"))
                if not isinstance(content, dict):
                    reasons.append("Estrutura do arquivo inválida: raiz JSON deve ser um objeto.")
                else:
                    # Validação exaustiva de todos os capítulos e todos os parágrafos
                    chapters = content.get("chapters")
                    if not isinstance(chapters, list) or len(chapters) == 0:
                        reasons.append("Arquivo não contém lista válida de capítulos no campo 'chapters'.")
                    else:
                        total_usable_paras = 0
                        for idx, ch in enumerate(chapters):
                            if not isinstance(ch, dict):
                                reasons.append(f"Capítulo no índice {idx} é inválido (deve ser um objeto dict).")
                                continue

                            raw_paras = ch.get("paragraphs")
                            text_block = ch.get("text_pt") or ch.get("text_en") or ch.get("text")
                            has_translation = ch.get("has_translation")

                            if raw_paras is not None:
                                if not isinstance(raw_paras, list):
                                    reasons.append(f"Capítulo no índice {idx}: 'paragraphs' deve ser uma lista.")
                                else:
                                    for p_idx, p in enumerate(raw_paras):
                                        if isinstance(p, str):
                                            if len(p.strip()) > 0:
                                                total_usable_paras += 1
                                            else:
                                                reasons.append(f"Capítulo no índice {idx}, parágrafo {p_idx} está vazio ou em branco.")
                                        elif isinstance(p, dict):
                                            p_text = p.get("text")
                                            if isinstance(p_text, str) and len(p_text.strip()) > 0:
                                                total_usable_paras += 1
                                            else:
                                                reasons.append(f"Capítulo no índice {idx}, parágrafo {p_idx} possui texto inválido ou ausente.")
                                        else:
                                            reasons.append(f"Capítulo no índice {idx}, parágrafo {p_idx} possui tipo inválido ({type(p).__name__}).")
                            elif text_block is not None:
                                if isinstance(text_block, str) and len(text_block.strip()) > 0:
                                    total_usable_paras += 1
                                elif has_translation is False:
                                    pass
                                else:
                                    reasons.append(f"Capítulo no índice {idx} possui bloco de texto vazio ou inválido.")
                            elif has_translation is False:
                                pass
                            else:
                                reasons.append(f"Capítulo no índice {idx} não contém nem lista 'paragraphs' nem bloco de texto.")

                        if total_usable_paras == 0 and not any("Capítulo no índice" in r for r in reasons):
                            reasons.append("Nenhum parágrafo ou texto utilizável foi encontrado nos capítulos.")

                    # Conferência estrita de metadados internos do arquivo JSON
                    file_meta = content.get("metadata")
                    if isinstance(file_meta, dict):
                        # 1. Correspondência exata de licença
                        file_lic = file_meta.get("license")
                        if file_lic and isinstance(file_lic, str):
                            if file_lic.strip() != declared_license_str:
                                reasons.append(
                                    f"Divergência de licença: arquivo declara '{file_lic.strip()}', "
                                    f"mas catálogo declara '{declared_license_str}'."
                                )

                        # 2. Identidade canônica da obra
                        file_id = file_meta.get("canonical_id") or file_meta.get("id")
                        if file_id and isinstance(file_id, str):
                            if file_id.strip() != work_id:
                                reasons.append(
                                    f"Divergência de identidade: arquivo identifica obra como '{file_id.strip()}', "
                                    f"mas catálogo referencia '{work_id}'."
                                )

                        # 3. Completude (completeness)
                        file_comp = file_meta.get("completeness")
                        if file_comp and isinstance(file_comp, str):
                            if file_comp.strip() != completeness_str:
                                reasons.append(
                                    f"Divergência de completude: arquivo declara '{file_comp.strip()}', "
                                    f"mas catálogo declara '{completeness_str}'."
                                )

                        # 4. Tipo de texto (text_type)
                        file_type = file_meta.get("text_type")
                        if file_type and isinstance(file_type, str):
                            if file_type.strip() != text_type_str:
                                reasons.append(
                                    f"Divergência de tipo de texto: arquivo declara '{file_type.strip()}', "
                                    f"mas catálogo declara '{text_type_str}'."
                                )

                if not reasons:
                    file_validated_successfully = True

            except Exception as e:
                reasons.append(f"Erro ao processar JSON do arquivo: {e}")
    elif require_file_exists:
        reasons.append("Arquivo local obrigatório não foi fornecido para auditoria.")

    # Determinação do Status
    if reasons:
        status = PromotionStatus.REJECTED
        is_promotable = False
    elif file_validated_successfully:
        if completeness_str == TextCompleteness.EXCERPT.value:
            status = PromotionStatus.APPROVED_EXCERPT
        elif completeness_str == TextCompleteness.ABRIDGED.value:
            status = PromotionStatus.APPROVED_ABRIDGED
        else:
            status = PromotionStatus.APPROVED
        is_promotable = True
    else:
        # Metadados e licença válidos, mas sem arquivo local validado
        status = PromotionStatus.CANDIDATE_ELIGIBLE
        is_promotable = True

    return PromotionEvaluation(
        work_id=work_id,
        status=status,
        is_promotable=is_promotable,
        reasons=reasons,
        warnings=warnings,
        metadata_snapshot={
            "title": work.get("title"),
            "author": work.get("author"),
            "license": declared_license_str,
            "completeness": completeness_str,
            "text_type": text_type_str,
            "source_edition": source_edition_str,
            "provenance_url": provenance_url_str
        }
    )


def audit_all_catalog_works(works_json_path: Path) -> List[PromotionEvaluation]:
    """Avalia todas as obras catalogadas em catalog/works.json segundo os critérios de promoção."""
    if not works_json_path.exists():
        raise FileNotFoundError(f"Catálogo de obras não encontrado: {works_json_path}")

    with open(works_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    works = data.get("works", [])
    evaluations: List[PromotionEvaluation] = []
    root = works_json_path.resolve().parent.parent

    # Carrega manifesto para validação criptográfica estrita
    corpus_approved_dir = (root / "corpus" / "approved").resolve()
    manifest_path = corpus_approved_dir / "manifest.json"
    manifest_hashes = load_manifest_hashes(manifest_path)

    for w in works:
        source_repo = w.get("source_repo", "")
        file_path = None
        expected_sha = None
        is_in_approved_corpus = False
        requires_manifest = False

        if source_repo and not source_repo.startswith("http://") and not source_repo.startswith("https://"):
            candidate_p = (root / source_repo).resolve()
            file_path = candidate_p

            try:
                rel_to_corpus = candidate_p.relative_to(corpus_approved_dir).as_posix()
                is_in_approved_corpus = True
                requires_manifest = True
                expected_sha = manifest_hashes.get(rel_to_corpus)
            except ValueError:
                # Arquivo local declarado FORA de corpus/approved (ex: data/sources, quarantine)
                is_in_approved_corpus = False
                requires_manifest = False
                expected_sha = None
        else:
            expected_sha = w.get("sha256")

        ev = evaluate_candidate_work(
            w,
            file_path=file_path,
            expected_sha=expected_sha,
            require_file_exists=is_in_approved_corpus,
            require_manifest_entry=requires_manifest,
            approved_corpus_root=corpus_approved_dir if file_path is not None else None
        )
        evaluations.append(ev)

    return evaluations
