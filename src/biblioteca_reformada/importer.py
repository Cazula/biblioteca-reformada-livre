"""Módulo de importação e normalização rigorosa de textos canônicos aprovados para SQLite."""

import json
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set
import sqlite3

from biblioteca_reformada.models import Verse, CANONICAL_BOOKS, resolve_canonical_book
from biblioteca_reformada.db import insert_verses_batch, reindex_fts
from biblioteca_reformada.licenses import load_manifest, ALLOWED_DISTRIBUTION_LICENSES

HEX64_REGEX = re.compile(r"^[0-9a-fA-F]{64}$")


def is_valid_sha256(val: Any) -> bool:
    """Verifica se o valor é uma string estritamente composta por 64 dígitos hexadecimais."""
    return isinstance(val, str) and bool(HEX64_REGEX.match(val.strip()))


class CorpusImportError(Exception):
    """Exceção levantada em caso de falha de validação ou importação de corpus."""
    pass


def parse_book_json(file_path: Path, expected_hash: Optional[str] = None) -> List[Verse]:
    """Valida e converte um arquivo JSON canônico em lista de objetos Verse com validação rigorosa.
    
    Lê o arquivo uma única vez como bytes, confere o hash SHA-256 e decodifica o JSON
    a partir do mesmo buffer em memória.
    """
    target = file_path.resolve()
    if not target.exists() or not target.is_file():
        raise CorpusImportError(f"Arquivo não encontrado ou inválido: {target}")

    # Validação do hash esperado caso fornecido
    if expected_hash is not None:
        if not is_valid_sha256(expected_hash):
            raise CorpusImportError(
                f"Hash SHA-256 esperado inválido: '{expected_hash}' (deve ter exatamente 64 dígitos hexadecimais)"
            )

    # Leitura atômica de buffer único em memória
    raw_bytes = target.read_bytes()
    actual_hash = hashlib.sha256(raw_bytes).hexdigest()

    if expected_hash is not None:
        if actual_hash.lower() != expected_hash.strip().lower():
            raise CorpusImportError(
                f"Hash SHA-256 adulterado para {target.name}: esperado {expected_hash}, obtido {actual_hash}"
            )

    try:
        content_str = raw_bytes.decode("utf-8")
        data = json.loads(content_str)
    except UnicodeDecodeError as ude:
        raise CorpusImportError(f"Arquivo {target} não é UTF-8 válido: {ude}")
    except json.JSONDecodeError as jde:
        raise CorpusImportError(f"Arquivo JSON corrompido em {target}: {jde}")

    if not isinstance(data, dict):
        raise CorpusImportError(f"Estrutura JSON inválida em {target}: raiz deve ser um objeto")

    # Validação do livro e conformidade com o cânon bíblico protestante
    book_raw = data.get("book")
    if not isinstance(book_raw, str) or not book_raw.strip():
        raise CorpusImportError(f"Campo 'book' ausente ou inválido em {target}")

    canonical_info = resolve_canonical_book(book_raw)
    if not canonical_info:
        raise CorpusImportError(f"Livro não reconhecido no cânon protestante de 66 livros: '{book_raw}' em {target}")

    canonical_book_name = canonical_info["name"]
    expected_testament = canonical_info["testament"]

    version_id = data.get("version")
    if not isinstance(version_id, str) or not version_id.strip():
        raise CorpusImportError(f"Campo 'version' ausente ou inválido em {target}")

    testament = data.get("testament")
    if testament not in ("AT", "NT"):
        raise CorpusImportError(f"Campo 'testament' deve ser 'AT' ou 'NT' em {target}")

    if testament != expected_testament:
        raise CorpusImportError(
            f"Incompatibilidade canônica de testamento para '{canonical_book_name}' em {target}: "
            f"esperado '{expected_testament}', obtido '{testament}'"
        )

    raw_chapters = data.get("chapters")
    if not isinstance(raw_chapters, list) or not raw_chapters:
        raise CorpusImportError(f"Nenhum capítulo válido encontrado em {target}")

    verses: List[Verse] = []
    seen_intra_book: Set[Tuple[int, int]] = set()

    for ch_idx, chap in enumerate(raw_chapters, start=1):
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
                version_id=version_id.strip(),
                testament=testament
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
                    f"Colisão/duplicação canônica detectada no corpus: versículo "
                    f"'{v.book} {v.chapter}:{v.verse}' (versão {v.version_id}) aparece repetido."
                )
            seen_global_keys[key] = v.text

        parsed_batches.append(verses)

    # Fase 2: Gravação atômica em lote com transação gerenciada externamente
    total_imported = 0
    try:
        with conn:
            for verses in parsed_batches:
                inserted = insert_verses_batch(conn, verses, sync_fts=False, in_transaction=True)
                total_imported += inserted

            # Sincroniza o índice FTS5 uma única vez em lote ao concluir a transação
            reindex_fts(conn, in_transaction=True)

    except Exception as exc:
        raise CorpusImportError(f"Falha atômica durante a importação do corpus: {exc}") from exc

    return total_imported
