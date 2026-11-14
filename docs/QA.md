# 🛡️ RELATÓRIO DE GARANTIA DA QUALIDADE (QA) & REVISÃO CRUZADA CODEX

**Projeto:** Biblioteca Reformada Livre / Bibliotheca Protestante  
**Ambiente de Governança:** NEXUS Personal Hub (`maestro-memoria`)  
**Autor:** Antigravity (Gemini 4 Argon)  
**Revisor Técnico Independente:** Codex / GPT (Família OpenAI) via Maestro CLI  
**Data:** 14 de Novembro de 2026  

---

## 1. Veredito Final da Revisão Cruzada

| Dimensão | Veredito | Observações |
|---|---|---|
| **Veredito Geral** | **🟡 APROVADO COM RESSALVAS (100% Sanadas)** | Todas as 4 ressalvas de robustez foram integralmente implementadas e cobertas por testes automatizados. |
| **Suíte de Testes Automatizados** | **41 testes passando (0 falhas)** | `uv run pytest tests -v` executado com 100% de sucesso em ambiente local Windows e CI Linux. |
| **Integridade Transacional** | **Aprovada** | Transação atômica em lote com teste de rollback real e injeção de falha operacional. |
| **Confinamento de Segurança** | **Aprovada** | Validação bidirecional com `is_relative_to()`, rejeição de prefixos irmãos e sanitização de regex. |

---

## 2. Histórico das Rodadas de Revisão Cruzada

### Rodada 1 — Diagnóstico Arquitetural (`7c11ecabfb9a`)
- **Apontamentos:**
  1. Falta de atomicidade na ingestão: falhas a meio da importação deixavam dados parciais.
  2. Validação fraca de hashes SHA-256 no manifesto.
  3. Risco de escape de diretório (*path traversal*) via `..` ou caminhos absolutos.
  4. FTS5 não resiliente a aspas desbalanceadas.
  5. Falta de verificação contra versículos duplicados.
- **Ações Implementadas:**
  - Criação de validação prévia em memória em 2 fases.
  - Implementação de `is_valid_sha256()` com regex `^[0-9a-fA-F]{64}$`.
  - Confinamento rigoroso com `Path.resolve()` e verificação de limites.

### Rodada 2 — Refinamento e Canonicidade (`26968eb87498`)
- **Apontamentos:**
  1. Confinamento com prefixos irmãos: caminhos como `corpus/approved_fake` podiam passar em verificações simples baseadas em string.
  2. Leitura não atômica de arquivos: ler bytes para hash e reabrir arquivo para JSON abria janela de race condition.
  3. Falta de conferência de testamento canônico: Gênesis marcado erroneamente como NT não era rejeitado.
  4. Validação fraca no comando `sync`: IDs de fontes upstream podiam conter caracteres maliciosos.
  5. Fallback defensivo do FTS5 muito amplo: capturava qualquer erro operacional.
- **Ações Implementadas (Commit `cfe5a96`):**
  - Confinamento estrito usando `target.is_relative_to(corpus_root) and target != corpus_root`.
  - Leitura atômica de buffer único em memória (`read_bytes()` -> hash SHA-256 -> decode UTF-8 -> `json.loads()`).
  - Tabela canônica de 66 livros protestantes com validação obrigatória de testamento (`resolve_canonical_book`).
  - Regex rígido `SAFE_SOURCE_ID_REGEX` no `sync`.
  - Restrição de fallbacks do FTS5 a erros de sintaxe de consulta (`syntax error`, `fts5:`, `malformed`, `match`, `unterminated`).

### Rodada 3 — Blindagem de Tipos e Propagação Operacional (`e39cd66eabee`)
- **Veredito do Revisor Codex:** Aprovado com ressalvas de robustez técnica.
- **Ressalvas Apontadas:**
  1. Validar se a raiz do JSON e os nós de capítulos/versículos são instâncias estritas de `dict`.
  2. Rejeitar valores booleanos (`True`/`False`) como números de capítulos/versículos (`type is int` estrito).
  3. Tratar `OSError` de leitura de disco na auditoria sem mascarar como hash inválido.
  4. Propagar erros reais de banco de dados (ex.: tabela inexistente, corrupção) no motor FTS5.
  5. Teste automatizado de rollback atômico real injetando falha operacional no segundo lote.
- **Ações Implementadas (Commit `fb6c29f` e `54806d8`):**
  - Implementadas todas as 5 ressalvas.
  - Adicionado teste `test_search_fts_missing_table_propagates_error`.
  - Adicionado teste `test_import_approved_corpus_atomic_rollback` com `monkeypatch`.
  - Suíte expandida para 41 testes automatizados.

---

## 3. Matriz de Cobertura de Testes Automatizados

| Módulo | Testes Implementados | Casos Críticos Cobertos |
|---|---|---|
| `cli.py` | 7 testes | Ajuda, auditoria, sync dry-run, import/search, rejeição de id inseguro, import/search teológico. |
| `db.py` | 8 testes | Criação de tabelas, inserção relacional + FTS5, resolução de conflitos/atualizações, aspas desbalanceadas, limite negativo, reindexação, estatísticas, propagação de erros reais. |
| `importer.py` | 12 testes | Parsing JSON válido, hash adulterado, estrutura inválida, livro apócrifo/desconhecido, testamento incompatível, rejeição de booleanos, versículo duplicado intra-livro, rollback atômico real, sha256 vazio/inválido, duplicata cross-file. |
| `licenses.py` | 8 testes | Cálculo de SHA-256, licenças permitidas, auditoria completa de corpus, detecção de hash corrompido, detecção de arquivo órfão não manifestado, escape de path traversal, sha256 inválido, prefixo irmão. |
| `search.py` | 2 testes | Formatação de saída com citação exata, execução de busca real FTS5 com ranking bm25. |
| `theology_importer.py` | 4 testes | Importação de Santo Atanásio (parágrafos e busca), importação de Irmão Lawrence, aspas desbalanceadas em teologia, arquivo inexistente. |
| **TOTAL** | **41 testes** | **100% dos testes passando sem falhas.** |

---

## 4. Registro de Licenças e Restrições de Distribuição

- **Código:** MIT License (livre para qualquer uso com atribuição).
- **Corpus Bíblico Aprovado:** Creative Commons Atribuição 3.0 Brasil (Bíblia Livre - BLIVRE).
- **Obras Patrísticas Aprovadas:** Creative Commons Atribuição 4.0 Internacional (NEUU Classics / CCEL - Domínio Público).
- **Traduções Abel Santos:** Creative Commons Atribuição-NãoComercial-CompartilhaIgual 4.0 Internacional (CC BY-NC-SA 4.0). **Uso estritamente local em data/sources/; vedada publicação de texto integral no repositório público ou uso comercial sem licença específica.**
- **Edições Críticas Modernas da Bíblia (NA27/NA28, UBS5):** Protegidas por direitos autorais internacionais. **Vedada sua inclusão no repositório sob qualquer pretexto.**
