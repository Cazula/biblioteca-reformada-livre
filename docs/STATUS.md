# 📊 STATUS DO PROJETO — Bibliotheca Protestante / Biblioteca Reformada Livre

**Data da Última Auditoria:** 14 de Novembro de 2026  
**Repositório Oficial:** [https://github.com/Cazula/biblioteca-reformada-livre](https://github.com/Cazula/biblioteca-reformada-livre)  
**Branch Principal:** `main`  
**Governança:** NEXUS Personal Hub & Cazula Engineering  

---

## 1. Resumo Executivo das Entregas

| Métrica / Dimensão | Estado Atual | Verificação / Evidência |
|---|---|---|
| **Suíte de Testes Automatizados** | **41 testes passando (100% verde)** | `uv run pytest tests -v` (7.30s) |
| **Obras Teológicas Catalogadas** | **12 obras registradas** | `catalog/works.json` |
| **Obras Aprovadas em Domínio Público** | **4 obras patrísticas e clássicas** | NEUU Classics (Atanásio, Anselmo, Kempis, Lawrence) |
| **Obras em Quarentena / Não Comerciais** | **8 obras locais** | Abel Santos (CC BY-NC-SA 4.0), CFW (sem licença), Scriptorium |
| **Corpus Bíblico Aprovado (Remoto)** | **5 livros canônicos seed (Obadias, Filemom, 2 e 3 João, Judas)** | `corpus/approved/bible/blivre/` com manifesto SHA-256 |
| **Corpus Bíblico Completo (Local)** | **66 livros da Bíblia Livre (31.100 versículos)** | `data/sources/blivre/` e `corpus/approved/bible/blivre/` |
| **Fontes Upstream Clonadas Localmente** | **12 repositórios completos + 1 parcial** | `data/sources/` (ignorado no Git público) |
| **Motor de Busca Textual FTS5** | **Operacional (Bíblia + Teologia: 1.573 parágrafos)** | `bref search` e `bref search-theology` |
| **Obras Teológicas Ingeridas no SQLite** | **4 obras clássicas (1.573 parágrafos indexados)** | Atanásio (98 §), Lawrence (179 §), Anselmo (342 §), Kempis (954 §) |
| **Pipeline de CI (GitHub Actions)** | **Verde / Corrigido** | Instalação editável `pip install -e .[dev]` + `pytest` + `bref audit` |
| **Revisão Cruzada Externa (Codex/Maestro)** | **Aprovado com Ressalvas (100% sanadas)** | ID `e39cd66eabee` registrado em `docs/QA.md` |

---

## 2. Inventário de Obras Teológicas (`catalog/works.json`)

### Obras Aprovadas para Distribuição Comercial e Pública
| ID da Obra | Título | Autor | Tradição | Licença | Origem / Edição-Base |
|---|---|---|---|---|---|
| `athanasius:incarnation` | *Da Encarnação do Verbo de Deus* | Santo Atanásio de Alexandria (c. 296–373) | Patrística | CC-BY-4.0 | CCEL (Archibald Robertson 1892, Domínio Público) / NEUU |
| `anselm:meditations` | *Orações e Meditações* | Santo Anselmo de Cantuária (1033–1109) | Escolástica Primitiva | CC-BY-4.0 | CCEL (Domínio Público) / NEUU |
| `kempis:imitation-of-christ` | *A Imitação de Cristo (Livro 1)* | Tomás de Kempis (1380–1471) | Devotio Moderna | CC-BY-4.0 | CCEL (Domínio Público) / NEUU |
| `lawrence:practice-presence-god` | *A Prática da Presença de Deus* | Irmão Lawrence (1614–1691) | Clássica Devocional | CC-BY-4.0 | Edição de 1692 (Domínio Público) / NEUU |

> **Nota de Revisão Humana:** As traduções acima foram produzidas pelo projeto editorial NEUU via pipeline de múltiplos passes (Claude Opus com glossário teológico) sob licença Creative Commons Atribuição 4.0. **Nenhuma obra deve ser classificada como revisada por especialista humano sem auditoria linha a linha explícita**; portanto, todas constam com `human_reviewed: false`.

### Obras Catalogadas em Quarentena Local (Não Distribuídas no Repositório Comercial)
| ID da Obra | Título | Autor | Tradição | Licença Declarada | Motivo da Quarentena |
|---|---|---|---|---|---|
| `westminster:cfw-abel` | *Confissão de Fé de Westminster (Tradução e Notas)* | Assembleia de Westminster | Puritana Presbiteriana | CC-BY-NC-SA-4.0 | Cláusula Não Comercial (NC): apenas metadados e links; vedada cópia de texto integral. |
| `hodge:commentary-wcf` | *Comentário sobre a Confissão de Fé* | A. A. Hodge (1823–1886) | Presbiteriana de Princeton | CC-BY-NC-SA-4.0 | Tradução em português sob CC BY-NC-SA. Texto original em inglês é Domínio Público. |
| `calvin:institutes` | *As Institutas da Religião Cristã* | João Calvino (1509–1564) | Reformada Magisterial | CC-BY-NC-SA-4.0 | Fragmentos traduzidos sob CC BY-NC-SA 4.0. |
| `calvin:ephesians-commentary` | *Comentário de Efésios* | João Calvino (1509–1564) | Reformada Magisterial | CC-BY-NC-SA-4.0 | Tradução sob CC BY-NC-SA 4.0. |
| `calvin:isaiah-ch7` | *Comentário de Isaías 7* | João Calvino (1509–1564) | Reformada Magisterial | CC-BY-NC-SA-4.0 | Tradução sob CC BY-NC-SA 4.0. |
| `caryl:job-exposition` | *Exposição sobre o Livro de Jó* | Joseph Caryl (1602–1673) | Puritana | CC-BY-NC-SA-4.0 | Tradução de capítulos sob CC BY-NC-SA 4.0. |
| `westminster:cfw-rickserrat` | *Confissão de Westminster (JSON)* | Assembleia de Westminster | Reformada Presbiteriana | Desconhecida / Nenhuma | Repositório upstream não fornece licença formal para a estruturação. |
| `scriptorium:divinum-corpus` | *Scriptorium Divinum Corpus* | Rilson Joás e colab. | Histórica | CC-BY-SA-4.0 | Clone raso parcial; edições-fonte não auditadas individualmente. |

---

## 3. Diagnóstico e Resolução da Integração Contínua (CI)

### Causas Concretas Diagnosticadas das Falhas Iniciais (Runs 1 a 14):
1. **Ausência de Instalação do Pacote:** O workflow inicial executava apenas `pip install pytest`, sem instalar a biblioteca local (`pip install -e .` ou `PYTHONPATH=.`), resultando em `ModuleNotFoundError: No module named 'biblioteca_reformada'`.
2. **Repositório Remoto sem Corpus Inicial:** A etapa `bref audit` do workflow exigia arquivos físicos para conferência dos hashes SHA-256 do manifesto; como o repositório remoto não possuía nenhum arquivo de texto em `corpus/approved/`, a auditoria falhava com erro de arquivo inexistente.
3. **Busca FTS5 sem Base Inicializada:** A chamada `bref search "verdade"` no workflow de teste tentava consultar tabelas virtuais antes que a ingestão criasse as tabelas.

### Correções Implementadas e Verificadas:
- Atualização de `.github/workflows/ci.yml`:
  - Matriz Python 3.10 a 3.13 no `ubuntu-latest`.
  - Instalação explícita com `pip install -e ".[dev]"`.
  - Execução controlada: `pytest -v`, `bref audit`, `bref import-blivre`, `bref index`, `bref search "verdade"` e `bref stats`.
- Envio atômico de corpus canônico representativo (`Obadias`, `Filemom`, `2 João`, `3 João`, `Judas`) com hashes SHA-256 rigorosamente auditados.

---

## 4. Status de Conformidade e Auditoria de Segurança

1. **Confinamento de Diretório:** Todas as operações de leitura e auditoria utilizam `Path.resolve()` e `is_relative_to()` para impedir ataques de *path traversal* (`..`) ou links simbólicos externos.
2. **Validação Estrita de SHA-256:** Hashes no manifesto devem ser strings hexadecimais estritas de exatamente 64 caracteres. Rejeição imediata de valores vazios, booleanos ou truncados.
3. **Atomicidade Transacional:** A ingestão relacional e a atualização do FTS5 são executadas em bloco transacional único gerenciado externamente; falha em qualquer obra provoca rollback completo e preserva a consistência do banco de dados.
4. **Isolamento de Fontes Upstream:** Pastas `data/sources/`, `scratch/` e bancos `.sqlite3` locais permanecem estritamente ignorados pelo Git (`.gitignore`).

---

## 5. Próximos Passos Prioritários

1. **Expansão do Corpus Teológico Aprovado:** Já concluída a importação integral das 4 primeiras obras clássicas (Atanásio, Anselmo, Kempis, Lawrence) totalizando 1.573 parágrafos indexados em FTS5. Próximo passo: incorporar o Livro 2 e Livro 3 da *Imitação de Cristo*.
2. **Auditoria Jurídica das Confissões de Westminster e Três Formas de Unidade:** Obter traduções em português de domínio público comprovado (ex.: edições históricas anteriores a 1950 ou traduções autorais sob licença MIT/CC BY).
3. **Frontend Interativo em Astro v5:** Criar leitor web leve e veloz com busca instantânea em milissegundos e visualização paralela de citações.
