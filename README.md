# 📖 Bibliotheca Protestante — Coleção Bibliotheca Reformata

[![CI](https://github.com/Cazula/biblioteca-reformada-livre/actions/workflows/ci.yml/badge.svg)](https://github.com/Cazula/biblioteca-reformada-livre/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Corpus License](https://img.shields.io/badge/Corpus%20License-CC%20BY%20%7C%20Public%20Domain-green.svg)](docs/legal/LICENSES.md)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Audit-74%20Files%20Verified-brightgreen.svg)](docs/STATUS.md)

Motor de busca textual ultrarrápido em SQLite FTS5, acervo bíblico integral (66 livros canônicos) e literatura teológica histórica clássica (Patrística, Luterana, Anglicana, Puritana e Batista Reformada), governado por políticas estritas de auditoria de licenças e proveniência criptográfica (SHA-256).

---

## 🌟 Visão e Identidade

A **Bibliotheca Protestante** é uma iniciativa de preservação digital, indexação lexical e recuperação teológica interdenominacional histórica, tendo a **Bibliotheca Reformata** como sua primeira coleção canônica.

1. **Legalidade e Direitos Inegociáveis:** Todo o código é livre sob licença **MIT**. Todos os textos distribuídos no repositório base possuem proveniência transparente:
   - Bíblia Livre (BLIVRE) sob **Creative Commons Atribuição 3.0 Brasil (CC BY 3.0 BR)**.
   - Clássicos históricos (Jonathan Edwards, Martinho Lutero, 39 Artigos Anglicanos, Confissão Batista de 1689) em **Domínio Público universal**.
   - Clássicos patrísticos e medievais (Atanásio, Anselmo, Kempis, Lawrence) sob **CC BY 4.0** (edições editoriais NEUU / CCEL).
   - Zero pirataria: traduções modernas sob copyright ou restrições não comerciais (ex.: Abel Santos CC BY-NC-SA) são catalogadas apenas com metadados e links em `catalog/works.json`, sem cópia de texto integral.
2. **Alta Performance Local:** Motor SQLite FTS5 nativo com tokenização Unicode e BM25, executando consultas em frações de milissegundo.
3. **Auditabilidade Criptográfica Bidirecional:** Cada arquivo possui hash SHA-256 verificado no manifesto. O comando `bref audit` valida integralmente a árvore de arquivos.
4. **Isolamento de Fontes:** Repositórios upstream e clones rasos residem estritamente em `data/sources/` (ignorado no Git).

---

## ⚙️ Instalação e Configuração

### Pré-requisitos
- Python 3.10 ou superior (testado no Python 3.10, 3.11, 3.12 e 3.13)
- [uv](https://github.com/astral-sh/uv) (recomendado) ou pip padrão

### Instalação Rápida
```powershell
git clone https://github.com/Cazula/biblioteca-reformada-livre.git
cd biblioteca-reformada-livre

# Criar ambiente virtual
uv venv
.venv\Scripts\activate

# Instalar em modo editável com dependências de desenvolvimento
uv pip install -e ".[dev]"
```

---

## 🚀 Guia de Uso da CLI (`bref`)

### 1. Auditoria Criptográfica e Jurídica
Audita todos os 74 arquivos do corpus aprovado (66 bíblicos + 8 teológicos) contra os hashes do manifesto:
```powershell
bref audit
```

### 2. Ingestão e Indexação Bíblica (66 Livros)
Importa os 66 livros da Bíblia Livre (31.100 versículos) para o SQLite FTS5:
```powershell
bref import-blivre
bref index
```

### 3. Ingestão de Obras Teológicas Aprovadas (8 Obras)
Ingere todo o acervo teológico aprovado (1.656 parágrafos) em lote:
```powershell
bref import-theology --all
```

### 4. Busca Textual na Escritura (com Citações Canônicas)
```powershell
bref search "verdade"
bref search "no princípio criou Deus"
bref search "justificados pela fé"
```

### 5. Busca Textual em Obras Teológicas Clássicas
```powershell
bref search-theology "inferno"
bref search-theology "mandamento"
bref search-theology "justificados somente pela fé"
bref search-theology "Verbo de Deus"
```
*Exemplo de saída de busca teológica com citação exata:*
```text
================================================================================
BIBLIOTECA REFORMADA LIVRE — BUSCA TEOLÓGICA FTS5
Consulta: "inferno" | Resultados encontrados: 3
================================================================================
[1] Igreja da Inglaterra (1571), Os Trinta e Nove Artigos de Religião, Artigos I a V, §3
    "Artigo III — Da Descida de Cristo ao Inferno: Assim como Cristo morreu por nós e foi sepultado..."

[2] Jonathan Edwards, Pecadores nas Mãos de um Deus Irado, Dez Considerações Doutrinárias, §1
    "1. Não falta poder a Deus para lançar os homens ímpios no inferno a qualquer momento..."
================================================================================
```

### 6. Estatísticas do Acervo
```powershell
bref stats
```

---

## 📚 Acervo Teológico Atual (`corpus/approved/theology/`)

| Obra | Autor | Tradição | Licença |
|---|---|---|---|
| *Pecadores nas Mãos de um Deus Irado* | Jonathan Edwards | Puritana Reformada | Public Domain |
| *O Catecismo Menor* | Martinho Lutero | Luterana Magistral | Public Domain |
| *Os Trinta e Nove Artigos de Religião* | Igreja da Inglaterra (1571) | Anglicana Reformada | Public Domain |
| *A Confissão de Fé Batista de 1689 (2LCF)* | Batistas Particulares (1689) | Batista Particular | Public Domain |
| *Da Encarnação do Verbo de Deus* | Santo Atanásio de Alexandria | Patrística Oriental | CC-BY-4.0 |
| *Orações e Meditações* | Santo Anselmo de Cantuária | Escolástica Primitiva | CC-BY-4.0 |
| *A Imitação de Cristo (Livro 1)* | Tomás de Kempis | Devotio Moderna | CC-BY-4.0 |
| *A Prática da Presença de Deus* | Irmão Lawrence | Clássica Devocional | CC-BY-4.0 |

---

## 🛡️ Governança e Transparência

- **CI / GitHub Actions:** A suíte de 47 testes passa 100% no ambiente local. O histórico de provisionamento remoto de runners e caminhos de resolução de billing na UI do GitHub estão detalhados em [docs/CI-BLOCKER.md](docs/CI-BLOCKER.md).
- **Inventário Completo de Obras:** Metadados e catálogo geral com status de quarentena em [catalog/works.json](catalog/works.json).
- **Status Executivo do Projeto:** Relatório detalhado em [docs/STATUS.md](docs/STATUS.md).
