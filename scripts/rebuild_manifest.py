"""Script para reconstruir integralmente o corpus/approved/manifest.json para Bíblia e Teologia."""

import hashlib
import json
from pathlib import Path


def compute_sha256(file_path: Path) -> str:
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def rebuild_manifest():
    root = Path(__file__).resolve().parent.parent
    approved_dir = root / "corpus" / "approved"
    manifest_path = approved_dir / "manifest.json"

    # Carregar metadados canônicos dos livros da Bíblia se existirem
    old_manifest_files = {}
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            old_data = json.load(f)
            for item in old_data.get("files", []):
                old_manifest_files[item["path"]] = item

    entries = []

    # 1. Livros da Bíblia (66 livros BLIVRE)
    bible_files = sorted(list((approved_dir / "bible" / "blivre").glob("*.json")))
    for bf in bible_files:
        rel_path = f"bible/blivre/{bf.name}"
        sha = compute_sha256(bf)
        old_entry = old_manifest_files.get(rel_path, {})
        book_name = old_entry.get("book") or bf.stem.split("-", 1)[-1].capitalize()
        testament = old_entry.get("testament")
        if not testament:
            num = int(bf.name.split("-")[0])
            testament = "AT" if num <= 39 else "NT"

        entries.append({
            "path": rel_path,
            "sha256": sha,
            "license": "CC-BY-3.0-BR",
            "book": book_name,
            "testament": testament
        })

    # 2. Obras Teológicas Aprovadas (8 obras)
    theology_files = sorted(list((approved_dir / "theology").glob("*.json")))
    theology_metadata = {
        "athanasius-incarnation.json": {
            "title": "Da Encarnação do Verbo de Deus",
            "author": "Santo Atanásio de Alexandria",
            "tradition": "Patrística",
            "license": "CC-BY-4.0"
        },
        "anselm-meditations.json": {
            "title": "Orações e Meditações",
            "author": "Santo Anselmo de Cantuária",
            "tradition": "Escolástica Primitiva",
            "license": "CC-BY-4.0"
        },
        "kempis-imitation.json": {
            "title": "A Imitação de Cristo (Livro 1)",
            "author": "Tomás de Kempis",
            "tradition": "Devotio Moderna",
            "license": "CC-BY-4.0"
        },
        "lawrence-practice.json": {
            "title": "A Prática da Presença de Deus",
            "author": "Irmão Lawrence",
            "tradition": "Clássica Devocional",
            "license": "CC-BY-4.0"
        },
        "edwards-sinners-angry-god.json": {
            "title": "Pecadores nas Mãos de um Deus Irado",
            "author": "Jonathan Edwards",
            "tradition": "Puritana Reformada",
            "license": "Public Domain"
        },
        "luther-small-catechism.json": {
            "title": "O Catecismo Menor",
            "author": "Martinho Lutero",
            "tradition": "Luterana Magistral",
            "license": "Public Domain"
        },
        "thirty-nine-articles.json": {
            "title": "Os Trinta e Nove Artigos de Religião",
            "author": "Igreja da Inglaterra (1571)",
            "tradition": "Anglicana Reformada",
            "license": "Public Domain"
        },
        "baptist-confession-1689.json": {
            "title": "A Confissão de Fé Batista de 1689",
            "author": "Batistas Particulares (1689)",
            "tradition": "Batista Particular Reformada",
            "license": "Public Domain"
        }
    }

    for tf in theology_files:
        rel_path = f"theology/{tf.name}"
        sha = compute_sha256(tf)
        info = theology_metadata.get(tf.name, {
            "title": tf.stem,
            "author": "Desconhecido",
            "tradition": "Clássica Cristã",
            "license": "Public Domain"
        })

        entries.append({
            "path": rel_path,
            "sha256": sha,
            "license": info["license"],
            "title": info["title"],
            "author": info["author"],
            "tradition": info["tradition"]
        })

    manifest = {
        "version": "1.1.0",
        "collection": "Bibliotheca Protestante — Coleção Bibliotheca Reformata",
        "generated_at": "2026-11-14T12:00:00Z",
        "canonical_system": "Protestant 66-book Canon + Classical Theological Corpus",
        "license_policy": "docs/legal/AUDIT_POLICY.md",
        "total_files": len(entries),
        "files": entries
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Manifesto reconstruído com sucesso em: {manifest_path}")
    print(f"Total de arquivos manifestados: {len(entries)} (Bíblia: {len(bible_files)}, Teologia: {len(theology_files)})")


if __name__ == "__main__":
    rebuild_manifest()