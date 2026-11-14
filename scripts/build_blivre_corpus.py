#!/usr/bin/env python3
"""Gera o acervo canônico aprovado de todos os 66 livros da Bíblia Livre (BLIVRE)."""

import hashlib
import json
import re
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "src"))

from biblioteca_reformada.models import CANONICAL_BOOKS, BOOK_BY_ID

blivre_txt_dir = root_dir / "data" / "sources" / "blivre" / "textos" / "f4" / "tr"
output_dir = root_dir / "corpus" / "approved" / "bible" / "blivre"
manifest_path = root_dir / "corpus" / "approved" / "manifest.json"


def clean_text(text: str) -> str:
    # Remove notas de rodapé (\fn ... \*fn)
    text = re.sub(r'\\fn.*?\*fn', '', text, flags=re.DOTALL)
    # Remove tags \added mas preserva as palavras adicionadas pelos tradutores
    text = re.sub(r'\\added\s*', '', text)
    text = re.sub(r'\\\*added', '', text)
    # Remove tags \psalm-title, \key, \ref
    text = re.sub(r'\\[a-zA-Z*_-]+', '', text)
    # Normaliza espaços em branco
    return re.sub(r'\s+', ' ', text).strip()


def slugify(name: str) -> str:
    s = name.lower()
    s = s.replace("ã", "a").replace("á", "a").replace("â", "a")
    s = s.replace("é", "e").replace("ê", "e")
    s = s.replace("í", "i")
    s = s.replace("ó", "o").replace("ô", "o").replace("õ", "o")
    s = s.replace("ú", "u")
    s = s.replace("ç", "c")
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s


def parse_blivre_file(file_path: Path) -> dict:
    raw = file_path.read_text(encoding="utf-8", errors="replace")

    # Extrai UBS code
    ubs_match = re.search(r'\\ubs-code\s*([\w]+)', raw)
    ubs_code = ubs_match.group(1).upper() if ubs_match else None

    # Extrai short name
    name_match = re.search(r'\\name-short\s*(.*?)\s*\\\*name-short', raw, re.DOTALL)
    short_name = name_match.group(1).strip() if name_match else None

    # Mapeia com CANONICAL_BOOKS
    book_meta = BOOK_BY_ID.get(ubs_code)
    if not book_meta:
        for b in CANONICAL_BOOKS:
            if b["name"].lower() == (short_name or "").lower():
                book_meta = b
                break

    canonical_name = book_meta["name"] if book_meta else (short_name or file_path.stem)
    testament = book_meta["testament"] if book_meta else ("NT" if "joao" in file_path.stem else "AT")
    order = book_meta["order"] if book_meta else 99
    abbr = book_meta["abbr"] if book_meta else ubs_code

    # Extrai versículos
    v_matches = re.findall(r'\\v\s+([a-zA-Z0-9]+)\.(\d+)\.(\d+)\s*\n(.*?)(?=\\v|\Z)', raw, flags=re.DOTALL)

    chapters_dict = {}
    for book_tag, ch_str, v_str, text_raw in v_matches:
        ch = int(ch_str)
        v = int(v_str)
        t = clean_text(text_raw)
        if not t:
            continue
        if ch not in chapters_dict:
            chapters_dict[ch] = []
        chapters_dict[ch].append({"verse": v, "text": t})

    chapters = []
    for ch in sorted(chapters_dict.keys()):
        chapters.append({
            "chapter": ch,
            "verses": chapters_dict[ch]
        })

    return {
        "version": "BLIVRE",
        "version_name": "Bíblia Livre (BLIVRE)",
        "language": "pt-BR",
        "license": "CC-BY-3.0-BR",
        "attribution": "Bíblia Livre (BLIVRE) por Diego Santos e colaboradores, sob licença Creative Commons Atribuição 3.0 Brasil (CC BY 3.0 BR).",
        "book": canonical_name,
        "book_abbr": abbr,
        "testament": testament,
        "order": order,
        "chapters": chapters
    }


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    if not blivre_txt_dir.exists():
        print(f"[ERRO] Diretório de textos BLIVRE não encontrado: {blivre_txt_dir}")
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)
    txt_files = list(blivre_txt_dir.glob("*.txt"))
    print(f"Encontrados {len(txt_files)} arquivos canônicos em {blivre_txt_dir}")

    manifest_entries = []
    total_verses = 0

    # Limpa arquivos antigos para garantir consistência
    for old_json in output_dir.glob("*.json"):
        old_json.unlink()

    parsed_books = []
    for f in txt_files:
        book_data = parse_blivre_file(f)
        parsed_books.append(book_data)

    # Ordena canonicamente (Gênesis 1 a Apocalipse 66)
    parsed_books.sort(key=lambda b: b.get("order", 99))

    for b in parsed_books:
        order = b["order"]
        slug = slugify(b["book"])
        filename = f"{order:02d}-{slug}.json"
        out_file = output_dir / filename

        verses_in_book = sum(len(ch["verses"]) for ch in b["chapters"])
        total_verses += verses_in_book

        with open(out_file, "w", encoding="utf-8") as f_out:
            json.dump(b, f_out, indent=2, ensure_ascii=False)
            f_out.write("\n")

        file_sha256 = compute_sha256(out_file)
        manifest_entries.append({
            "path": f"bible/blivre/{filename}",
            "sha256": file_sha256,
            "license": "CC-BY-3.0-BR",
            "source_id": "blivre",
            "book": b["book"],
            "verses_count": verses_in_book,
            "testament": b["testament"],
            "attribution": "Bíblia Livre (BLIVRE) por Diego Santos e colaboradores, CC BY 3.0 BR."
        })
        print(f"  [OK] Livro {order:02d}: {b['book']} ({verses_in_book} versículos) -> {filename}")

    # Salva o manifesto de proveniência atualizado
    manifest_data = {
        "version": "1.0.0",
        "generated_at": "2026-11-14T00:50:00Z",
        "project": "Biblioteca Reformada Livre",
        "total_books": len(manifest_entries),
        "total_verses": total_verses,
        "files": manifest_entries
    }

    with open(manifest_path, "w", encoding="utf-8") as f_m:
        json.dump(manifest_data, f_m, indent=2, ensure_ascii=False)
        f_m.write("\n")

    print("\n" + "=" * 80)
    print(f"SUCESSO: {len(manifest_entries)} livros canônicos gerados com {total_verses} versículos!")
    print(f"Manifesto salvo em: {manifest_path}")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
