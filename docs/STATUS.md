# 📊 STATUS DO PROJETO — Bibliotheca Protestante / Biblioteca Reformada Livre

**Data da Última Auditoria:** 14 de Novembro de 2026  
**Repositório Oficial:** [https://github.com/Cazula/biblioteca-reformada-livre](https://github.com/Cazula/biblioteca-reformada-livre)  
**Branch Principal:** `main`  
**Governança:** NEXUS Personal Hub & Cazula Engineering  

---

## 1. Resumo Executivo das Entregas e Verificabilidade

| Métrica / Dimensão | Estado Atual | Verificação / Evidência |
|---|---|---|
| **Suíte de Testes Automatizados** | **47 testes passando (100% verde)** | `uv run pytest tests -v` (6.86s) |
| **Arquivos no Manifesto de Proveniência** | **74 arquivos auditados com SHA-256** | `corpus/approved/manifest.json` |
| **Corpus Bíblico Aprovado (Bíblia Livre)** | **66 livros canônicos (31.100 versículos)** | `corpus/approved/bible/blivre/*.json` (CC BY 3.0 BR) |
| **Corpus Teológico Aprovado (Versionado)** | **8 obras clássicas e históricas (1.656 parágrafos)** | `corpus/approved/theology/*.json` (Domínio Público e CC BY 4.0) |
| **Inventário Geral de Obras Teológicas** | **18 obras registradas** | `catalog/works.json` (8 aprovadas, 2 candidatas PD, 8 em quarentena) |
| **Motor de Busca Textual FTS5** | **Bíblia + Literatura Teológica Operacional** | `bref search` e `bref search-theology` com BM25 |
| **Sincronização Upstream (`bref sync`)** | **Clone seguro com subprocess e validação de URL** | `SAFE_SOURCE_ID_REGEX` e verificação de scheme `https://` |
| **Status da CI Remota (GitHub Actions)** | **Bloqueio Externo de Runners / Provisionamento** | 0 steps, 404 BlobNotFound, Run ID 43560233382 (ver `docs/CI-BLOCKER.md`) |
| **Revisão Cruzada Externa (Codex/Maestro)** | **Aprovado com Ressalvas (100% sanadas)** | ID `e39cd66eabee` registrado em `docs/QA.md` |

---

## 2. Inventário de Obras Teológicas Aprovadas (`corpus/approved/theology/`)

Todas as 8 obras abaixo possuem arquivos JSON estruturados por capítulos e parágrafos, hashes criptográficos SHA-256 validados no manifesto e indexação instantânea no motor FTS5:

| ID da Obra | Título | Autor / Origem | Tradição | Licença | Parágrafos FTS5 |
|---|---|---|---|---|---|
| `edwards:sinners-in-the-hands-of-an-angry-god` | *Pecadores nas Mãos de um Deus Irado* | Jonathan Edwards (1703–1758) | Puritana Reformada | CC-BY-4.0 (Extrato) | 20 § |
| `luther:small-catechism` | *O Catecismo Menor* | Martinho Lutero (1483–1546) | Luterana Magistral | CC-BY-4.0 (Seleção) | 31 § |
| `anglican:thirty-nine-articles` | *Os Trinta e Nove Artigos de Religião* | Igreja da Inglaterra (1571) | Anglicana Reformada | CC-BY-4.0 (Seleção) | 19 § |
| `baptist:confession-1689` | *A Confissão de Fé Batista de 1689 (2LCF)* | Batistas Particulares (1689) | Batista Particular Reformada | CC-BY-4.0 (Extrato) | 13 § |
| `athanasius:incarnation` | *Da Encarnação do Verbo de Deus* | Santo Atanásio de Alexandria (c. 296–373) | Patrística Oriental | CC-BY-4.0 (Integral) | 98 § |
| `anselm:meditations` | *Orações e Meditações de Santo Anselmo* | Santo Anselmo de Cantuária (1033–1109) | Escolástica Primitiva | CC-BY-4.0 (Integral) | 342 § |
| `kempis:imitation-of-christ` | *A Imitação de Cristo (Livro 1)* | Tomás de Kempis (1380–1471) | Devotio Moderna | CC-BY-4.0 (Livro 1) | 954 § |
| `lawrence:practice-presence-god` | *A Prática da Presença de Deus* | Irmão Lawrence (1614–1691) | Clássica Devocional | CC-BY-4.0 (Integral) | 179 § |

> **Total no FTS5:** **1.656 parágrafos teológicos** e **31.100 versículos bíblicos**.  
> **Transparência Editorial e Proveniência:** As 4 obras em português de Edwards, Lutero, 39 Artigos e Confissão de 1689 são extratos/paráfrases doutrinárias representativas sob CC-BY-4.0 (as edições originais históricas de 1741/1529/1571/1689 permanecem em Domínio Público universal). Os 4 clássicos NEUU (Atanásio, Anselmo, Kempis e Lawrence) são traduções completas provenientes do dataset editorial NEUU sob CC-BY-4.0. Todas as obras possuem `human_reviewed: false`.

---

## 3. Obras Candidatas e Matriz de Quarentena (`catalog/works.json`)

### Obras Candidatas de Domínio Público (Originais Ingleses Verificados)
- **`calvin:institutes-allen-1816`** — *Institutas da Religião Cristã* (João Calvino, Tradução John Allen, 1813/1816). Edição em Domínio Público universal (Projeto Gutenberg eBook #45001, Vol. 1 de 2). Nota bibliográfica corrigida: não confundir com a tradução posterior de Henry Beveridge (1845). Candidata prioritária para tradução e ingestão estruturada.
- **`bunyan:pilgrims-progress-1678`** — *O Peregrino* (John Bunyan, 1678). Edição histórica original de Nathaniel Ponder em Domínio Público universal (Projeto Gutenberg eBook #131).

### Obras em Quarentena Local (Restrição Jurídica / Não Comerciais)
- **Abel Santos (CC BY-NC-SA 4.0):** 6 obras catalogadas (Confissão de Westminster, Comentário de A.A. Hodge, Institutas, Comentários de Efésios e Isaías 7, Exposição de Jó por Joseph Caryl). Apenas links e metadados constam no catálogo público; nenhum texto integral copiado.
- **CFW JSON (rickserrat):** Retido por ausência de licença formal declarada no upstream.
- **Scriptorium Divinum:** Retido por clone parcial (.git apenas) e dependência de auditoria individual de fontes.

---

## 4. Diagnóstico Factual da CI (GitHub Actions)

A infraestrutura remota do GitHub Actions apresenta **falha de provisionamento anterior à execução de etapas** (`startup_failure`):
- **Evidências Empíricas:** Execuções com duração de 1–3 segundos, `steps: []` (0 passos executados), e endpoint de logs retornando HTTP 404 `BlobNotFound`.
- **Esclarecimento de Cota:** De acordo com a documentação oficial do GitHub, repositórios públicos possuem runners `ubuntu-latest` gratuitos e ilimitados. A falha decorre de causa indeterminada no provisionamento pré-runner (políticas de ações da conta ou restrição temporária do pool do GitHub).
- **Documento de Auditoria e Resolução:** [docs/CI-BLOCKER.md](file:///I:/Nexus/PROJETOS/ATIVOS/BIBLIOTECA-REFORMADA-LIVRE/docs/CI-BLOCKER.md).
- **Validação Local:** A suíte de 47 testes passa 100% no ambiente local com Python 3.13 (`pytest tests -v` e `bref audit`). O workflow remoto `.github/workflows/ci.yml` foi mantido sem mascaramento de erros.

---

## 5. Comandos da CLI (`bref`)

```powershell
# 1. Auditoria jurídica e de integridade dos 74 arquivos do corpus aprovado
uv run bref audit

# 2. Ingestão dos 66 livros da Bíblia Livre (31.100 versículos) para SQLite FTS5
uv run bref import-blivre

# 3. Ingestão de todo o acervo teológico aprovado (8 obras, 1.656 parágrafos)
uv run bref import-theology --all

# 4. Busca textual com citações canônicas de versículos
bref search "no princípio criou Deus"

# 5. Busca textual com citações de obras teológicas clássicas
bref search-theology "inferno"
bref search-theology "mandamento"
bref search-theology "justificados somente pela fé"

# 6. Painel consolidado de estatísticas de acervo
uv run bref stats
```
