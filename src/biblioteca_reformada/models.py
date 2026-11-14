"""Modelos de dados canônicos da Biblioteca Reformada Livre."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class Verse:
    """Representa um versículo bíblico canônico com proveniência de tradução."""
    book: str
    chapter: int
    verse: int
    text: str
    version_id: str = "BLIVRE"
    testament: str = "NT"  # "AT" ou "NT"
    id: Optional[int] = None

    @property
    def reference(self) -> str:
        """Retorna a citação canônica exata (ex.: '3 João 1:4')."""
        return f"{self.book} {self.chapter}:{self.verse}"

    def to_citation(self) -> str:
        """Formata citação completa com versão."""
        return f"[{self.reference}] {self.text} ({self.version_id})"


@dataclass
class SearchResult:
    """Resultado estruturado de uma busca textual FTS5."""
    book: str
    chapter: int
    verse: int
    text: str
    version_id: str
    rank: float = 0.0

    @property
    def reference(self) -> str:
        return f"{self.book} {self.chapter}:{self.verse}"

    def to_citation(self) -> str:
        return f"[{self.reference}] {self.text} ({self.version_id})"


@dataclass
class Document:
    """Documento teológico ou confessional."""
    id: str
    title: str
    author: str
    category: str
    license: str
    content: str
    source_url: Optional[str] = None


@dataclass
class TheologicalDocument:
    """Representa uma obra teológica ou patrística completa com metadados editoriais."""
    id: str
    work_id: str
    title: str
    author: str
    tradition: str
    category: str
    language: str
    license: str
    attribution: str
    chapters_count: int = 0
    paragraphs_count: int = 0


@dataclass
class TheologicalParagraph:
    """Representa um parágrafo/seção indexável de uma obra teológica."""
    id: str
    document_id: str
    work_id: str
    chapter_num: int
    chapter_title: str
    paragraph_num: int
    paragraph_id: str
    text: str
    language: str
    citation: str


@dataclass
class TheologicalSearchResult:
    """Resultado estruturado de busca textual em obras teológicas FTS5."""
    document_id: str
    work_id: str
    author: str
    title: str
    chapter_num: int
    chapter_title: str
    paragraph_num: int
    citation: str
    text: str
    rank: float = 0.0



CANONICAL_BOOKS: List[Dict[str, Any]] = [
    # Antigo Testamento (39)
    {"id": "GEN", "name": "Gênesis", "abbr": "Gn", "testament": "AT", "order": 1},
    {"id": "EXO", "name": "Êxodo", "abbr": "Êx", "testament": "AT", "order": 2},
    {"id": "LEV", "name": "Levítico", "abbr": "Lv", "testament": "AT", "order": 3},
    {"id": "NUM", "name": "Números", "abbr": "Nm", "testament": "AT", "order": 4},
    {"id": "DEU", "name": "Deuteronômio", "abbr": "Dt", "testament": "AT", "order": 5},
    {"id": "JOS", "name": "Josué", "abbr": "Js", "testament": "AT", "order": 6},
    {"id": "JDG", "name": "Juízes", "abbr": "Jz", "testament": "AT", "order": 7},
    {"id": "RUT", "name": "Rute", "abbr": "Rt", "testament": "AT", "order": 8},
    {"id": "1SA", "name": "1 Samuel", "abbr": "1Sm", "testament": "AT", "order": 9},
    {"id": "2SA", "name": "2 Samuel", "abbr": "2Sm", "testament": "AT", "order": 10},
    {"id": "1KI", "name": "1 Reis", "abbr": "1Rs", "testament": "AT", "order": 11},
    {"id": "2KI", "name": "2 Reis", "abbr": "2Rs", "testament": "AT", "order": 12},
    {"id": "1CH", "name": "1 Crônicas", "abbr": "1Cr", "testament": "AT", "order": 13},
    {"id": "2CH", "name": "2 Crônicas", "abbr": "2Cr", "testament": "AT", "order": 14},
    {"id": "EZR", "name": "Esdras", "abbr": "Ed", "testament": "AT", "order": 15},
    {"id": "NEH", "name": "Neemias", "abbr": "Ne", "testament": "AT", "order": 16},
    {"id": "EST", "name": "Ester", "abbr": "Et", "testament": "AT", "order": 17},
    {"id": "JOB", "name": "Jó", "abbr": "Jó", "testament": "AT", "order": 18},
    {"id": "PSA", "name": "Salmos", "abbr": "Sl", "testament": "AT", "order": 19},
    {"id": "PRO", "name": "Provérbios", "abbr": "Pv", "testament": "AT", "order": 20},
    {"id": "ECC", "name": "Eclesiastes", "abbr": "Ec", "testament": "AT", "order": 21},
    {"id": "SNG", "name": "Cântico dos Cânticos", "abbr": "Ct", "testament": "AT", "order": 22},
    {"id": "ISA", "name": "Isaías", "abbr": "Is", "testament": "AT", "order": 23},
    {"id": "JER", "name": "Jeremias", "abbr": "Jr", "testament": "AT", "order": 24},
    {"id": "LAM", "name": "Lamentações", "abbr": "Lm", "testament": "AT", "order": 25},
    {"id": "EZK", "name": "Ezequiel", "abbr": "Ez", "testament": "AT", "order": 26},
    {"id": "DAN", "name": "Daniel", "abbr": "Dn", "testament": "AT", "order": 27},
    {"id": "HOS", "name": "Oseias", "abbr": "Os", "testament": "AT", "order": 28},
    {"id": "JOL", "name": "Joel", "abbr": "Jl", "testament": "AT", "order": 29},
    {"id": "AMO", "name": "Amós", "abbr": "Am", "testament": "AT", "order": 30},
    {"id": "OBA", "name": "Obadias", "abbr": "Ob", "testament": "AT", "order": 31},
    {"id": "JON", "name": "Jonas", "abbr": "Jn", "testament": "AT", "order": 32},
    {"id": "MIC", "name": "Miqueias", "abbr": "Mq", "testament": "AT", "order": 33},
    {"id": "NAM", "name": "Naum", "abbr": "Na", "testament": "AT", "order": 34},
    {"id": "HAB", "name": "Habacuque", "abbr": "Hc", "testament": "AT", "order": 35},
    {"id": "ZEP", "name": "Sofonias", "abbr": "Sf", "testament": "AT", "order": 36},
    {"id": "HAG", "name": "Ageu", "abbr": "Ag", "testament": "AT", "order": 37},
    {"id": "ZEC", "name": "Zacarias", "abbr": "Zc", "testament": "AT", "order": 38},
    {"id": "MAL", "name": "Malaquias", "abbr": "Ml", "testament": "AT", "order": 39},
    # Novo Testamento (27)
    {"id": "MAT", "name": "Mateus", "abbr": "Mt", "testament": "NT", "order": 40},
    {"id": "MRK", "name": "Marcos", "abbr": "Mc", "testament": "NT", "order": 41},
    {"id": "LUK", "name": "Lucas", "abbr": "Lc", "testament": "NT", "order": 42},
    {"id": "JHN", "name": "João", "abbr": "Jo", "testament": "NT", "order": 43},
    {"id": "ACT", "name": "Atos", "abbr": "At", "testament": "NT", "order": 44},
    {"id": "ROM", "name": "Romanos", "abbr": "Rm", "testament": "NT", "order": 45},
    {"id": "1CO", "name": "1 Coríntios", "abbr": "1Co", "testament": "NT", "order": 46},
    {"id": "2CO", "name": "2 Coríntios", "abbr": "2Co", "testament": "NT", "order": 47},
    {"id": "GAL", "name": "Gálatas", "abbr": "Gl", "testament": "NT", "order": 48},
    {"id": "EPH", "name": "Efésios", "abbr": "Ef", "testament": "NT", "order": 49},
    {"id": "PHP", "name": "Filipenses", "abbr": "Fp", "testament": "NT", "order": 50},
    {"id": "COL", "name": "Colossenses", "abbr": "Cl", "testament": "NT", "order": 51},
    {"id": "1TH", "name": "1 Tessalonicenses", "abbr": "1Ts", "testament": "NT", "order": 52},
    {"id": "2TH", "name": "2 Tessalonicenses", "abbr": "2Ts", "testament": "NT", "order": 53},
    {"id": "1TI", "name": "1 Timóteo", "abbr": "1Tm", "testament": "NT", "order": 54},
    {"id": "2TI", "name": "2 Timóteo", "abbr": "2Tm", "testament": "NT", "order": 55},
    {"id": "TIT", "name": "Tito", "abbr": "Tt", "testament": "NT", "order": 56},
    {"id": "PHM", "name": "Filemom", "abbr": "Fm", "testament": "NT", "order": 57},
    {"id": "HEB", "name": "Hebreus", "abbr": "Hb", "testament": "NT", "order": 58},
    {"id": "JAS", "name": "Tiago", "abbr": "Tg", "testament": "NT", "order": 59},
    {"id": "1PE", "name": "1 Pedro", "abbr": "1Pe", "testament": "NT", "order": 60},
    {"id": "2PE", "name": "2 Pedro", "abbr": "2Pe", "testament": "NT", "order": 61},
    {"id": "1JN", "name": "1 João", "abbr": "1Jo", "testament": "NT", "order": 62},
    {"id": "2JN", "name": "2 João", "abbr": "2Jo", "testament": "NT", "order": 63},
    {"id": "3JN", "name": "3 João", "abbr": "3Jo", "testament": "NT", "order": 64},
    {"id": "JUD", "name": "Judas", "abbr": "Jd", "testament": "NT", "order": 65},
    {"id": "REV", "name": "Apocalipse", "abbr": "Ap", "testament": "NT", "order": 66},
]

BOOK_BY_NAME = {b["name"].lower(): b for b in CANONICAL_BOOKS}
BOOK_BY_ABBR = {b["abbr"].lower(): b for b in CANONICAL_BOOKS}
BOOK_BY_ID = {b["id"]: b for b in CANONICAL_BOOKS}


def resolve_canonical_book(name_or_abbr: str) -> Optional[Dict[str, Any]]:
    """Resolve e valida um livro contra o cânon protestante de 66 livros."""
    if not isinstance(name_or_abbr, str):
        return None
    clean = name_or_abbr.strip()
    if not clean:
        return None
    if clean.upper() in BOOK_BY_ID:
        return BOOK_BY_ID[clean.upper()]
    lower = clean.lower()
    if lower in BOOK_BY_NAME:
        return BOOK_BY_NAME[lower]
    if lower in BOOK_BY_ABBR:
        return BOOK_BY_ABBR[lower]
    return None
