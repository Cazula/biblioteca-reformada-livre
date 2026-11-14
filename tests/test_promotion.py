"""Testes automatizados dos critérios de promoção canônica, integridade criptográfica e governança editorial."""

import hashlib
import json
from pathlib import Path
import pytest

from biblioteca_reformada.promotion import (
    evaluate_candidate_work,
    audit_all_catalog_works,
    PromotionStatus,
    TextCompleteness,
    TextType
)


def test_evaluate_candidate_work_valid_full(tmp_path):
    target = tmp_path / "valid_full.json"
    content = {
        "metadata": {"title": "Da Encarnação", "license": "CC-BY-4.0"},
        "chapters": [{"number": 1, "title": "Criação", "paragraphs": ["No princípio era o Verbo."]}]
    }
    raw_bytes = json.dumps(content).encode("utf-8")
    target.write_bytes(raw_bytes)
    sha = hashlib.sha256(raw_bytes).hexdigest()

    work = {
        "work_id": "test:athanasius",
        "title": "Da Encarnação",
        "author": "Atanásio",
        "license": "CC-BY-4.0",
        "completeness": "full",
        "text_type": "translation",
        "source_edition": "Archibald Robertson (1892, Domínio Público)",
        "provenance_url": "https://github.com/neuu-org/bible-classics-dataset",
        "sha256": sha,
        "human_reviewed": False
    }
    ev = evaluate_candidate_work(work, file_path=target, expected_sha=sha)
    assert ev.is_promotable is True
    assert ev.status == PromotionStatus.APPROVED
    assert len(ev.reasons) == 0


def test_evaluate_candidate_work_valid_excerpt(tmp_path):
    target = tmp_path / "valid_excerpt.json"
    content = {
        "metadata": {"title": "Pecadores", "license": "CC-BY-4.0"},
        "chapters": [{"number": 1, "title": "Deuteronômio", "paragraphs": ["A seu tempo o pé deles resvalará."]}]
    }
    raw_bytes = json.dumps(content).encode("utf-8")
    target.write_bytes(raw_bytes)
    sha = hashlib.sha256(raw_bytes).hexdigest()

    work = {
        "work_id": "test:edwards",
        "title": "Pecadores",
        "author": "Edwards",
        "license": "CC-BY-4.0",
        "completeness": "excerpt",
        "text_type": "paraphrase",
        "source_edition": "Boston 1741, Domínio Público; Gutenberg #34632",
        "provenance_url": "https://www.gutenberg.org/ebooks/34632",
        "sha256": sha,
        "human_reviewed": False
    }
    ev = evaluate_candidate_work(work, file_path=target, expected_sha=sha)
    assert ev.is_promotable is True
    assert ev.status == PromotionStatus.APPROVED_EXCERPT
    assert len(ev.reasons) == 0


def test_evaluate_candidate_work_abridged_classification(tmp_path):
    target = tmp_path / "valid_abridged.json"
    content = {
        "metadata": {"title": "Abreviado", "license": "CC-BY-4.0"},
        "chapters": [{"number": 1, "paragraphs": ["Resumo do capítulo."]}]
    }
    raw_bytes = json.dumps(content).encode("utf-8")
    target.write_bytes(raw_bytes)
    sha = hashlib.sha256(raw_bytes).hexdigest()

    work = {
        "work_id": "test:abridged",
        "title": "Obra Abreviada",
        "author": "Autor",
        "license": "CC-BY-4.0",
        "completeness": "abridged",
        "text_type": "translation",
        "source_edition": "Edição Histórica (1850)",
        "provenance_url": "https://example.com/abridged",
        "sha256": sha
    }
    # Quando allow_excerpts=True, classifica como APPROVED_ABRIDGED
    ev_allowed = evaluate_candidate_work(work, file_path=target, allow_excerpts=True, expected_sha=sha)
    assert ev_allowed.is_promotable is True
    assert ev_allowed.status == PromotionStatus.APPROVED_ABRIDGED

    # Quando allow_excerpts=False, rejeita expressamente
    ev_strict = evaluate_candidate_work(work, file_path=target, allow_excerpts=False, expected_sha=sha)
    assert ev_strict.is_promotable is False
    assert ev_strict.status == PromotionStatus.REJECTED
    assert any("abridged" in r for r in ev_strict.reasons)


def test_evaluate_candidate_work_rejects_non_string_or_empty_types():
    """Garante que metadados malformados (int, list, etc.) geram impedimento e não quebram a auditoria."""
    work_numeric_fields = {
        "work_id": "test:numeric",
        "title": "Tipos Errados",
        "author": "Autor",
        "license": ["CC-BY-4.0"],  # lista ao invés de string
        "completeness": 123,       # número ao invés de string
        "text_type": None,
        "source_edition": 1850,    # número ao invés de string
        "provenance_url": 999.9    # float ao invés de string
    }
    ev = evaluate_candidate_work(work_numeric_fields)
    assert ev.is_promotable is False
    assert ev.status == PromotionStatus.REJECTED
    assert len(ev.reasons) >= 4


def test_evaluate_candidate_work_rejects_missing_or_malformed_expected_sha(tmp_path):
    target = tmp_path / "content.json"
    target.write_text(json.dumps({"chapters": [{"paragraphs": ["Texto"]}]}), encoding="utf-8")

    work = {
        "work_id": "test:bad-sha",
        "title": "SHA Malformado",
        "author": "Autor",
        "license": "CC-BY-4.0",
        "completeness": "full",
        "text_type": "translation",
        "source_edition": "Edição Histórica (1850)",
        "provenance_url": "https://example.com"
    }

    # Hash curto
    ev_short = evaluate_candidate_work(work, file_path=target, expected_sha="abcdef")
    assert ev_short.is_promotable is False
    assert any("malformado" in r for r in ev_short.reasons)

    # Hash com caracteres não hexadecimais
    ev_non_hex = evaluate_candidate_work(work, file_path=target, expected_sha="z" * 64)
    assert ev_non_hex.is_promotable is False
    assert any("malformado" in r for r in ev_non_hex.reasons)


def test_evaluate_candidate_work_rejects_missing_declared_local_file(tmp_path):
    missing_target = tmp_path / "does_not_exist.json"
    work = {
        "work_id": "test:missing-file",
        "title": "Arquivo Inexistente",
        "author": "Autor",
        "license": "CC-BY-4.0",
        "completeness": "full",
        "text_type": "translation",
        "source_edition": "Edição Histórica (1850)",
        "provenance_url": "https://example.com"
    }
    ev = evaluate_candidate_work(work, file_path=missing_target)
    assert ev.is_promotable is False
    assert ev.status == PromotionStatus.REJECTED
    assert any("não encontrado" in r for r in ev.reasons)


def test_evaluate_candidate_work_rejects_invalid_schema_chapters_and_paragraphs(tmp_path):
    target = tmp_path / "bad_schema.json"
    # chapters como string ao invés de lista de dicts
    target.write_text(json.dumps({"chapters": "invalido"}), encoding="utf-8")

    work = {
        "work_id": "test:bad-schema",
        "title": "Esquema Ruim",
        "author": "Autor",
        "license": "CC-BY-4.0",
        "completeness": "full",
        "text_type": "translation",
        "source_edition": "Edição Histórica (1850)",
        "provenance_url": "https://example.com"
    }
    ev = evaluate_candidate_work(work, file_path=target)
    assert ev.is_promotable is False
    assert any("lista válida de capítulos" in r for r in ev.reasons)

    # chapters com parágrafos vazios ou sem texto
    target.write_text(json.dumps({"chapters": [{"title": "C1", "paragraphs": ["   ", ""]}]}), encoding="utf-8")
    ev2 = evaluate_candidate_work(work, file_path=target)
    assert ev2.is_promotable is False
    assert any("está vazio ou em branco" in r for r in ev2.reasons)


def test_evaluate_candidate_work_rejects_mismatched_metadata_license(tmp_path):
    target = tmp_path / "mismatched.json"
    # Arquivo declara licença restrita CC-BY-NC enquanto catálogo alega CC-BY-4.0
    content = {
        "metadata": {"title": "Divergente", "license": "CC-BY-NC-4.0"},
        "chapters": [{"number": 1, "paragraphs": ["Texto qualquer."]}]
    }
    target.write_text(json.dumps(content), encoding="utf-8")

    work = {
        "work_id": "test:mismatched-lic",
        "title": "Licença Divergente",
        "author": "Autor",
        "license": "CC-BY-4.0",
        "completeness": "full",
        "text_type": "translation",
        "source_edition": "Edição Histórica (1850)",
        "provenance_url": "https://example.com"
    }
    ev = evaluate_candidate_work(work, file_path=target)
    assert ev.is_promotable is False
    assert any("Divergência de licença" in r for r in ev.reasons)


def test_evaluate_candidate_work_rejects_noncommercial_license():
    work = {
        "work_id": "test:cfw-nc",
        "title": "Confissão",
        "author": "Westminster",
        "license": "CC-BY-NC-SA-4.0",
        "completeness": "full",
        "text_type": "translation",
        "source_edition": "Westminster (1646); Tradução Abel Santos",
        "provenance_url": "https://github.com/separovichabel/abel-santos"
    }
    ev = evaluate_candidate_work(work)
    assert ev.is_promotable is False
    assert ev.status == PromotionStatus.REJECTED
    assert any("não permitida" in r for r in ev.reasons)


def test_evaluate_candidate_work_rejects_missing_provenance_url():
    work = {
        "work_id": "test:no-url",
        "title": "Obra Sem URL",
        "author": "Autor",
        "license": "CC-BY-4.0",
        "completeness": "full",
        "text_type": "translation",
        "source_edition": "Edição Histórica (1850)",
        "provenance_url": ""
    }
    ev = evaluate_candidate_work(work)
    assert ev.is_promotable is False
    assert any("URL de proveniência ausente" in r for r in ev.reasons)


def test_evaluate_candidate_work_rejects_unsafe_provenance_url():
    work = {
        "work_id": "test:unsafe-url",
        "title": "Obra URL Insegura",
        "author": "Autor",
        "license": "CC-BY-4.0",
        "completeness": "full",
        "text_type": "translation",
        "source_edition": "Edição Histórica (1850)",
        "provenance_url": "ftp://ftp.example.com/obra"
    }
    ev = evaluate_candidate_work(work)
    assert ev.is_promotable is False
    assert any("esquema inseguro" in r for r in ev.reasons)


def test_evaluate_candidate_work_rejects_missing_source_edition():
    work = {
        "work_id": "test:no-edition",
        "title": "Sem Edição",
        "author": "Autor",
        "license": "CC-BY-4.0",
        "completeness": "full",
        "text_type": "translation",
        "source_edition": "",
        "provenance_url": "https://example.com"
    }
    ev = evaluate_candidate_work(work)
    assert ev.is_promotable is False
    assert any("Edição-fonte primária ausente" in r for r in ev.reasons)


def test_evaluate_candidate_work_rejects_modern_pt_translation_claiming_pd():
    work = {
        "work_id": "test:fake-pd",
        "title": "Institutas Traduzidas Hoje",
        "author": "Calvino",
        "license": "Public Domain",
        "completeness": "full",
        "text_type": "translation",
        "language": "pt-BR",
        "source_edition": "Genebra 1559",
        "provenance_url": "https://example.com"
    }
    ev = evaluate_candidate_work(work)
    assert ev.is_promotable is False
    assert any("Inconsistência de direitos" in r for r in ev.reasons)


def test_evaluate_candidate_work_with_corrupted_file(tmp_path):
    bad_file = tmp_path / "corrupted.json"
    bad_file.write_text("not json content", encoding="utf-8")

    work = {
        "work_id": "test:corrupted",
        "title": "Corrompido",
        "author": "Autor",
        "license": "CC-BY-4.0",
        "completeness": "full",
        "text_type": "translation",
        "source_edition": "Edição 1900",
        "provenance_url": "https://example.com"
    }
    ev = evaluate_candidate_work(work, file_path=bad_file)
    assert ev.is_promotable is False
    assert any("Erro ao processar JSON" in r for r in ev.reasons)


def test_evaluate_candidate_work_with_hash_mismatch(tmp_path):
    valid_json = tmp_path / "valid.json"
    valid_json.write_text(json.dumps({"chapters": [{"paragraphs": ["Texto"]}]}), encoding="utf-8")

    work = {
        "work_id": "test:hash-mismatch",
        "title": "Hash Errado",
        "author": "Autor",
        "license": "CC-BY-4.0",
        "completeness": "full",
        "text_type": "translation",
        "source_edition": "Edição 1900",
        "provenance_url": "https://example.com",
        "sha256": "0" * 64
    }
    ev = evaluate_candidate_work(work, file_path=valid_json, expected_sha="0" * 64)
    assert ev.is_promotable is False
    assert any("Divergência de hash SHA-256" in r for r in ev.reasons)


def test_audit_all_catalog_works_real_catalog_indexed_and_strict():
    """Valida rigorosamente as 18 obras do catálogo oficial indexadas por work_id."""
    root = Path(__file__).resolve().parent.parent
    works_path = root / "catalog" / "works.json"
    assert works_path.exists()

    evaluations = audit_all_catalog_works(works_path)
    assert len(evaluations) == 18

    eval_by_id = {ev.work_id: ev for ev in evaluations}
    assert len(eval_by_id) == 18

    # 1. Quatro Clássicos NEUU Integrais no Corpus (devem ser APPROVED com arquivo e hash no manifesto)
    neuu_ids = [
        "athanasius:incarnation",
        "anselm:meditations",
        "kempis:imitation",
        "lawrence:practice"
    ]
    for wid in neuu_ids:
        assert wid in eval_by_id, f"Obra {wid} não encontrada no catálogo"
        ev = eval_by_id[wid]
        assert ev.status == PromotionStatus.APPROVED
        assert ev.is_promotable is True
        assert len(ev.reasons) == 0

    # 2. Quatro Extratos Doutrinários Aprovados no Corpus (devem ser APPROVED_EXCERPT)
    excerpt_ids = [
        "edwards:sinners-in-the-hands-of-an-angry-god",
        "luther:small-catechism",
        "anglican:thirty-nine-articles",
        "baptist:confession-1689"
    ]
    for wid in excerpt_ids:
        assert wid in eval_by_id, f"Obra {wid} não encontrada no catálogo"
        ev = eval_by_id[wid]
        assert ev.status == PromotionStatus.APPROVED_EXCERPT
        assert ev.is_promotable is True
        assert len(ev.reasons) == 0

    # 3. Duas Obras Candidatas Integrais em Catálogo (Gutenberg EN, pendentes de ingestão local)
    candidate_ids = [
        "calvin:institutes-allen-1816",
        "bunyan:pilgrims-progress-1678"
    ]
    for wid in candidate_ids:
        assert wid in eval_by_id, f"Obra {wid} não encontrada no catálogo"
        ev = eval_by_id[wid]
        assert ev.status == PromotionStatus.CANDIDATE_ELIGIBLE
        assert ev.is_promotable is True
        assert len(ev.reasons) == 0

    # 4. Seis Obras Abel Santos sob licença CC-BY-NC-SA-4.0 (devem ser explicitamente REJECTED)
    abel_nc_ids = [
        "westminster:cfw-abel",
        "hodge:commentary-wcf",
        "calvin:institutas-abel",
        "calvin:comentario-efesios-abel",
        "calvin:comentario-isaias-7-abel",
        "caryl:exposition-job-abel"
    ]
    for wid in abel_nc_ids:
        assert wid in eval_by_id, f"Obra {wid} não encontrada no catálogo"
        ev = eval_by_id[wid]
        assert ev.status == PromotionStatus.REJECTED
        assert ev.is_promotable is False
        assert any("CC-BY-NC-SA-4.0" in r for r in ev.reasons)

    # 5. Duas Obras Retidas por licença não especificada ou em auditoria
    other_quarantine_ids = [
        "westminster:cfw-json-rickserrat",
        "scriptorium:scriptorium-divinum"
    ]
    for wid in other_quarantine_ids:
        assert wid in eval_by_id, f"Obra {wid} não encontrada no catálogo"
        ev = eval_by_id[wid]
        assert ev.status == PromotionStatus.REJECTED
        assert ev.is_promotable is False


def test_evaluate_candidate_work_rejects_missing_manifest_entry_for_approved_corpus(tmp_path):
    target = tmp_path / "orphan.json"
    content = {
        "metadata": {"title": "Orfão", "license": "CC-BY-4.0"},
        "chapters": [{"number": 1, "paragraphs": ["Texto legítimo."]}]
    }
    raw_bytes = json.dumps(content).encode("utf-8")
    target.write_bytes(raw_bytes)
    sha = hashlib.sha256(raw_bytes).hexdigest()

    work = {
        "work_id": "test:orphan",
        "title": "Arquivo Órfão",
        "author": "Autor",
        "license": "CC-BY-4.0",
        "completeness": "full",
        "text_type": "translation",
        "source_edition": "Edição Histórica (1850)",
        "provenance_url": "https://example.com",
        "sha256": sha
    }
    # Quando require_manifest_entry=True e expected_sha=None (não encontrado no manifesto)
    ev = evaluate_candidate_work(
        work,
        file_path=target,
        expected_sha=None,
        require_file_exists=True,
        require_manifest_entry=True
    )
    assert ev.is_promotable is False
    assert ev.status == PromotionStatus.REJECTED
    assert any("não registrado no manifesto imutável manifest.json" in r for r in ev.reasons)


def test_evaluate_candidate_work_rejects_confinement_violation(tmp_path):
    approved_dir = tmp_path / "approved"
    approved_dir.mkdir()
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()

    outside_file = outside_dir / "escaped.json"
    content = {
        "metadata": {"title": "Fuga", "license": "CC-BY-4.0"},
        "chapters": [{"number": 1, "paragraphs": ["Texto fora do corpus."]}]
    }
    raw_bytes = json.dumps(content).encode("utf-8")
    outside_file.write_bytes(raw_bytes)
    sha = hashlib.sha256(raw_bytes).hexdigest()

    work = {
        "work_id": "test:escaped",
        "title": "Arquivo Fora do Corpus",
        "author": "Autor",
        "license": "CC-BY-4.0",
        "completeness": "full",
        "text_type": "translation",
        "source_edition": "Edição Histórica (1850)",
        "provenance_url": "https://example.com",
        "sha256": sha
    }
    ev = evaluate_candidate_work(
        work,
        file_path=outside_file,
        expected_sha=sha,
        approved_corpus_root=approved_dir
    )
    assert ev.is_promotable is False
    assert ev.status == PromotionStatus.REJECTED
    assert any("Violação de confinamento" in r for r in ev.reasons)


def test_evaluate_candidate_work_rejects_internal_metadata_divergences(tmp_path):
    target = tmp_path / "divergent.json"
    # Arquivo declara licença Apache-2.0, completeness excerpt e text_type paraphrase
    content = {
        "metadata": {
            "canonical_id": "test:another-id",
            "license": "Apache-2.0",
            "completeness": "excerpt",
            "text_type": "paraphrase"
        },
        "chapters": [{"number": 1, "paragraphs": ["Texto de teste."]}]
    }
    raw_bytes = json.dumps(content).encode("utf-8")
    target.write_bytes(raw_bytes)
    sha = hashlib.sha256(raw_bytes).hexdigest()

    work = {
        "work_id": "test:correct-id",
        "title": "Catálogo Alega CC-BY-4.0 e Full",
        "author": "Autor",
        "license": "CC-BY-4.0",
        "completeness": "full",
        "text_type": "translation",
        "source_edition": "Edição Histórica (1850)",
        "provenance_url": "https://example.com",
        "sha256": sha
    }
    ev = evaluate_candidate_work(work, file_path=target, expected_sha=sha)
    assert ev.is_promotable is False
    assert ev.status == PromotionStatus.REJECTED
    # Verifica que todas as 4 divergências foram apontadas
    assert any("Divergência de licença" in r for r in ev.reasons)
    assert any("Divergência de identidade" in r for r in ev.reasons)
    assert any("Divergência de completude" in r for r in ev.reasons)
    assert any("Divergência de tipo de texto" in r for r in ev.reasons)


def test_evaluate_candidate_work_rejects_mixed_valid_and_invalid_paragraphs(tmp_path):
    target = tmp_path / "mixed_paras.json"
    # Capítulo 1 com texto legítimo, Capítulo 2 com parágrafo numérico e nulo
    content = {
        "metadata": {"title": "Misto", "license": "CC-BY-4.0"},
        "chapters": [
            {"number": 1, "paragraphs": ["Parágrafo perfeito e válido."]},
            {"number": 2, "paragraphs": ["Primeiro parágrafo válido", 12345, None]}
        ]
    }
    raw_bytes = json.dumps(content).encode("utf-8")
    target.write_bytes(raw_bytes)
    sha = hashlib.sha256(raw_bytes).hexdigest()

    work = {
        "work_id": "test:mixed",
        "title": "Parágrafos Mistos",
        "author": "Autor",
        "license": "CC-BY-4.0",
        "completeness": "full",
        "text_type": "translation",
        "source_edition": "Edição Histórica (1850)",
        "provenance_url": "https://example.com",
        "sha256": sha
    }
    ev = evaluate_candidate_work(work, file_path=target, expected_sha=sha)
    assert ev.is_promotable is False
    assert ev.status == PromotionStatus.REJECTED
    assert any("parágrafo 1 possui tipo inválido" in r for r in ev.reasons)
    assert any("parágrafo 2 possui tipo inválido" in r for r in ev.reasons)

