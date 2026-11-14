"""Importador de acervos bíblicos auditados para o SQLite relacional."""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple

from biblioteca_reformada.models import Verse
from biblioteca_reformada.licenses import (
    compute_sha256,
    is_valid_sha256,
    load_manifest,
    ALLOWED_DISTRIBUTION_LICENSES
)
from biblioteca_reformada.db import insert_verses_batch

PROTESTANT_CANON = {
    # Antigo Testamento (39)
    "Gênesis", "Êxodo", "Levítico", "Números", "Deuteronômio",
    "Josué", "Juízes", "Rute", "1 Samuel", "2 Samuel",
    "1 Reis", "2 Reis", "1 Crônicas", "2 Crônicas", "Esdras",
    "Neemias", "Ester", "Jó", "Salmos", "Provérbios",
    "Eclesiastes", "Cânticos", "Isaías", "Jeremias", "Lamentações",
    "Ezequiel", "Daniel", "Oséias", "Joel", "Amós",
    "Obadias", "Jonas", "Miquéias", "Naum", "Habacuque",
    "Sofonias", "Ageu", "Zacarias", "Malaquias",
    # Novo Testamento (27)
    "Mateus", "Marcos", "Lucas", "João", "Atos",
    "Romanos", "1 Coríntios", "2 Coríntios", "Gálatas", "Efésios",
    "Filipenses", "Colossenses", "1 Tessalonicenses", "2 Tessalonicenses",
    "1 Timóteo", "2 Timóteo", "Tito", "Filemom", "Hebreus",
    "Tiago", "1 Pedro", "2 Pedro", "1 João", "2 João",
    "3 João", "Judas", "Apocalipse"
}

OLD_TESTAMENT = set(list(PROTESTANT_CANON)[:39])
NEW_TESTAMENT = set(list(PROTESTANT_CANON)[39:])


class CorpusImportError(Exception):
    """Exceção levantada quando um arquivo de corpus viola integridade, formato ou licença."""
    pass


def parse_book_json(file_path: Path, expected_hash: Optional[str] = None) -> List[Verse]:
    """Lê, valida a integridade do hash e normaliza um livro da Bíblia Livre em JSON."""
    target = file_path.resolve()
    if not target.exists() or not target.is_file():
        raise CorpusImportError(f"Arquivo não encontrado: {target}")

    if expected_hash:
        actual_hash = compute_sha256(target)
        if actual_hash.strip().lower() != expected_hash.strip().lower():
            raise CorpusImportError(
                f"Corrupção de integridade em {target.name}: hash obtido '{actual_hash}' diverge do manifesto '{expected_hash}'"
            )

    try:
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as jde:
        raise CorpusImportError(f"Arquivo JSON corrompido em {target}: {jde}")

    if not isinstance(data, dict):
        raise CorpusImportError(f"Estrutura JSON inválida em {target}: raiz deve ser um objeto")

    # Validação do livro e conformidade com o cânon bíblico protestante
    book_raw = data.get("book")
    if not isinstance(book_raw, str) or not book_raw.strip():
        raise CorpusImportError(f"Campo 'book' ausente ou inválido em {target}")

    canonical_book_name = book_raw.strip()
    if canonical_book_name not in PROTESTANT_CANON:
        raise CorpusImportError(
            f"Livro '{canonical_book_name}' em {target} não pertence ao cânon bíblico protestante aceito."
        )

    version_id = data.get("version", "BLIVRE")
    declared_testament = data.get("testament")
    expected_testament = "AT" if canonical_book_name in OLD_TESTAMENT else "NT"

    if declared_testament and declared_testament != expected_testament:
        raise CorpusImportError(
            f"Incompatibilidade testamentária para {canonical_book_name}: declarado {declared_testament}, esperado {expected_testament}"
        )

    chapters = data.get("chapters")
    if not isinstance(chapters, list) or not chapters:
        raise CorpusImportError(f"Nenhum capítulo encontrado no livro {canonical_book_name} ({target})")

    verses: List[Verse] = []
    seen_intra_book: Set[Tuple[int, int]] = set()

    for ch_idx, chap in enumerate(chapters, start=1):
        if not isinstance(chap, dict):
            raise CorpusImportError(f"Estrutura inválida no capítulo {ch_idx} de {target}: deve ser um objeto JSON")

        ch_num = chap.get("chapter")
        # type is int estrito (rejeita booleano como True/False que herdam de int)
        if type(ch_num) is not int or ch_num <= 0:
            raise CorpusImportError(
                f"Número de capítulo inválido ({ch_num!r}) no índice {ch_idx} de {target}: "
                f"deve ser inteiro estritamente positivo (não booleano)"
            )

        raw_verses = chap.get("verses")
        if not isinstance(raw_verses, list) or not raw_verses:
            raise CorpusImportError(f"Capítulo {ch_num} sem versículos em {target}")

        for v_idx, v in enumerate(raw_verses, start=1):
            if not isinstance(v, dict):
                raise CorpusImportError(
                    f"Estrutura inválida no versículo {v_idx} do capítulo {ch_num} de {target}: deve ser um objeto JSON"
                )

            v_num = v.get("verse")
            if type(v_num) is not int or v_num <= 0:
                raise CorpusImportError(
                    f"Versículo inválido ({v_num!r}) no capítulo {ch_num} de {target}: "
                    f"deve ser inteiro estritamente positivo (não booleano)"
                )

            ref_key = (ch_num, v_num)
            if ref_key in seen_intra_book:
                raise CorpusImportError(
                    f"Versículo duplicado no arquivo {target.name}: capítulo {ch_num}, versículo {v_num}"
                )
            seen_intra_book.add(ref_key)

            text = v.get("text")
            if not isinstance(text, str) or not text.strip():
                raise CorpusImportError(f"Texto vazio no versículo {ch_num}:{v_num} de {target}")

            verses.append(Verse(
                book=canonical_book_name,
                chapter=ch_num,
                verse=v_num,
                text=text.strip(),
                version_id=version_id,
                testament=expected_testament
            ))

    return verses


def import_approved_corpus(
    corpus_approved_dir: Path,
    conn: sqlite3.Connection,
    manifest_path: Optional[Path] = None
) -> int:
    """Importa com validação criptográfica obrigatória somente arquivos listados e aprovados no manifesto.
    
    Garante:
    1. Confinamento absoluto dentro de corpus_approved_dir com Path.is_relative_to().
    2. Validação obrigatória de sha256 (64 dígitos hex).
    3. Detecção e rejeição de versículos duplicados no corpus antes de qualquer gravação.
    4. Atomicidade completa: em caso de falha em qualquer obra, nenhum dado persiste no banco.
    """
    corpus_root = corpus_approved_dir.resolve()
    manifest_file = manifest_path.resolve() if manifest_path else (corpus_root / "manifest.json")

    if not manifest_file.exists():
        raise CorpusImportError(f"Manifesto de proveniência não encontrado: {manifest_file}")

    try:
        manifest = load_manifest(manifest_file)
    except Exception as exc:
        raise CorpusImportError(f"Falha ao ler ou decodificar o manifesto {manifest_file}: {exc}") from exc

    if not isinstance(manifest, dict):
        raise CorpusImportError(f"Estrutura do manifesto inválida em {manifest_file}: raiz deve ser um objeto JSON")

    entries = manifest.get("files")
    if not isinstance(entries, list) or not entries:
        raise CorpusImportError("Manifesto vazio ou inválido: nenhuma obra aprovada para importação.")

    parsed_batches: List[List[Verse]] = []
    seen_global_keys: Dict[Tuple[str, int, int, str], str] = {}

    # Fase 1: Validação rigorosa de todos os arquivos em memória antes de tocar no banco
    for entry in entries:
        if not isinstance(entry, dict):
            raise CorpusImportError("Entrada inválida no manifesto: cada item deve ser um objeto JSON.")

        rel_path = entry.get("path")
        if not rel_path or not isinstance(rel_path, str) or not rel_path.strip():
            raise CorpusImportError("Entrada no manifesto com campo 'path' ausente ou inválido.")

        # Obras teológicas possuem schema e importador próprio (theology_importer.py); são ignoradas no import bíblico
        if rel_path.startswith("theology/") or "/theology/" in rel_path:
            continue

        p_rel = Path(rel_path)
        if p_rel.is_absolute() or ".." in p_rel.parts:
            raise CorpusImportError(f"Caminho absoluto ou travessia '..' proibida no manifesto: {rel_path}")

        target_file = (corpus_root / rel_path).resolve()
        if not target_file.is_relative_to(corpus_root) or target_file == corpus_root:
            raise CorpusImportError(f"Tentativa de escape de diretório fora de corpus/approved: {rel_path}")

        expected_hash = entry.get("sha256")
        if not is_valid_sha256(expected_hash):
            raise CorpusImportError(
                f"Entrada no manifesto para '{rel_path}' rejeitada: 'sha256' ausente, vazio ou inválido "
                f"(deve ser string hexadecimal de 64 caracteres)."
            )

        declared_license = entry.get("license")
        if declared_license not in ALLOWED_DISTRIBUTION_LICENSES:
            raise CorpusImportError(
                f"Obra {rel_path} rejeitada: licença '{declared_license}' não permitida para distribuição."
            )

        verses = parse_book_json(target_file, expected_hash=expected_hash)

        # Verificação de duplicatas e colisões no corpus inteiro
        for v in verses:
            key = (v.book, v.chapter, v.verse, v.version_id)
            if key in seen_global_keys:
                raise CorpusImportError(
                    f"Conflito de integridade: versículo {v.book} {v.chapter}:{v.verse} ({v.version_id}) "
                    f"duplicado entre os arquivos '{seen_global_keys[key]}' e '{target_file.name}'."
                )
            seen_global_keys[key] = target_file.name

        parsed_batches.append(verses)

    # Fase 2: Gravação atômica real em transação isolada
    total_imported = 0
    with conn:
        for batch in parsed_batches:
            try:
                # sync_fts=False durante o loop de lote; reindexação atômica ao final
                inserted = insert_verses_batch(conn, batch, sync_fts=False, in_transaction=True)
                total_imported += inserted
            except Exception as exc:
                # Transação com 'with conn:' executa rollback automático em exceção não capturada
                raise CorpusImportError(f"Falha operacional ao persistir lote no banco de dados: {exc}") from exc

        # Reconstrói FTS5 atomicamente dentro da mesma transação
        from biblioteca_reformada.db import reindex_fts
        reindex_fts(conn, in_transaction=True)

    return total_imported
