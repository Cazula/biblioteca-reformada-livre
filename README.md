# 📖 Bibliotheca Reformata — Biblioteca Reformada Livre

**Uma biblioteca teológica protestante, reformada e puritana em software livre, local-first e auditável.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![License: CC BY 3.0 BR](https://img.shields.io/badge/Corpus-CC%20BY%203.0%20BR-green.svg)](docs/legal/LICENSES.md)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](pyproject.toml)
[![SQLite: FTS5](https://img.shields.io/badge/Engine-SQLite%20FTS5-orange.svg)](src/biblioteca_reformada/db.py)

---

## 🎯 Visão do Projeto

A **Biblioteca Reformada Livre** é um ecossistema digital para preservação, estudo, busca textual avançada e catalogação da literatura bíblica e teológica da **Reforma Protestante** (Tradições Reformada/Presbiteriana, Puritana, Luterana Magistral e Batista Particular).

### Pilares Fundamentais:
1. **Local-First & Preservação Digital:** Funciona totalmente offline em banco SQLite com motor de busca de texto completo (FTS5). Não depende de servidores proprietários ou serviços de terceiros para operar.
2. **Governança de Licenças e Domínio Público:** Distinção rigorosa entre obras em Domínio Público universal, traduções sob Creative Commons (CC BY, CC BY-SA) e materiais retidos em **quarentena local** (CC BY-NC, CC BY-NC-ND ou sem autorização explícita para redistribuição comercial/derivada).
3. **Auditoria Criptográfica:** Todo arquivo aprovado possui hash SHA-256 verificado em manifesto imutável (`corpus/approved/manifest.json`). Qualquer corrupção ou adulteração de dados é bloqueada na ingestão.
4. **Semântica e Precisão Reformada:** Vocabulário teológico canônico, estrutura canônica de 66 livros e catálogo de confissões históricas (Westminster, 1689, Trinta e Nove Artigos, Cânones de Dort, Catecismo Menor).

---

## 🚀 Instalação Rápida

O projeto utiliza o gerenciador de pacotes ultrarrápido **`uv`** (Rust):

```powershell
# 1. Clone o repositório
git clone https://github.com/Cazula/biblioteca-reformada-livre.git
cd biblioteca-reformada-livre

# 2. Crie o ambiente virtual e instale as dependências
uv sync

# 3. Execute a suíte de testes (47 testes unitários e de integração)
uv run pytest tests -v
```

---

## 💻 Guia da CLI (`bref`)

A interface de linha de comando (`bref`) oferece ferramentas completas para auditoria, importação e consulta:

### 1. Auditoria de Licenças e Integridade
Verifica se todos os arquivos do corpus aprovado correspondem aos seus hashes SHA-256 e licenças permitidas:
```powershell
bref audit
```

### 2. Ingestão da Bíblia Livre (66 Livros)
Importa os 31.100 versículos canônicos da Bíblia Livre (CC BY 3.0 BR) para o SQLite local e reconstrói o índice FTS5:
```powershell
bref import-blivre
```

### 3. Ingestão do Acervo Teológico Histórico
Importa as obras teológicas clássicas aprovadas (Patrística, Escolástica, Reformada, Puritana e Luterana):
```powershell
bref import-theology --all
```

### 4. Busca Textual Bíblica (FTS5)
Permite buscar termos, expressões compostas e prefixos com citações canônicas de livro, capítulo e versículo:
```powershell
bref search "no princípio criou Deus"
bref search "justificado pela fé" --limit 5
bref search "amor" --testament NT
```
*Exemplo de saída:*
```text
================================================================================
BIBLIOTECA REFORMADA LIVRE — RESULTADOS DA BUSCA FTS5
Consulta: "no princípio criou Deus" | Resultados encontrados: 1
================================================================================
[1] Gênesis 1:1 (BLIVRE - AT)
    "No princípio criou Deus os céus e a terra."
================================================================================
```

### 5. Busca Textual Teológica Clássica
Realiza busca de texto completo nas obras teológicas com citações estruturadas de autor, obra, capítulo e parágrafo:
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

| Obra | Autor | Tradição | Licença / Status |
|---|---|---|---|
| *Pecadores nas Mãos de um Deus Irado* | Jonathan Edwards | Puritana Reformada | CC-BY-4.0 (Extrato Selecionado) |
| *O Catecismo Menor* | Martinho Lutero | Luterana Magistral | CC-BY-4.0 (Seleção Doutrinária) |
| *Os Trinta e Nove Artigos de Religião* | Igreja da Inglaterra (1571) | Anglicana Reformada | CC-BY-4.0 (Seleção Doutrinária) |
| *A Confissão de Fé Batista de 1689 (2LCF)* | Batistas Particulares (1689) | Batista Particular | CC-BY-4.0 (Extrato de 4 Capítulos) |
| *Da Encarnação do Verbo de Deus* | Santo Atanásio de Alexandria | Patrística Oriental | CC-BY-4.0 (Tradução Integral) |
| *Orações e Meditações* | Santo Anselmo de Cantuária | Escolástica Primitiva | CC-BY-4.0 (Tradução Integral) |
| *A Imitação de Cristo (Livro 1)* | Tomás de Kempis | Devotio Moderna | CC-BY-4.0 (Tradução Livro 1) |
| *A Prática da Presença de Deus* | Irmão Lawrence | Clássica Devocional | CC-BY-4.0 (Tradução Integral) |

---

## 🛡️ Governança e Transparência

- **CI / GitHub Actions:** A suíte de 47 testes passa 100% no ambiente local. O diagnóstico factual de provisionamento pré-runner no GitHub está documentado em [docs/CI-BLOCKER.md](docs/CI-BLOCKER.md).
- **Inventário Completo de Obras:** Metadados e catálogo geral com status de quarentena em [catalog/works.json](catalog/works.json).
- **Status Executivo do Projeto:** Relatório detalhado em [docs/STATUS.md](docs/STATUS.md).
