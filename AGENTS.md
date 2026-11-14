# 🤖 AGENTS.md — Diretrizes de Operação da Biblioteca Reformada Livre

Este documento estabelece as regras vitais e operacionais para agentes de Inteligência Artificial (Gemini, Claude, Hermes, Codex e subagentes) atuando no repositório **Biblioteca Reformada Livre**.

---

## 1. Princípios Inegociáveis

1. **Idioma Obrigatório:** Toda a comunicação, commits, logs e documentações devem ser exclusivamente em **Português do Brasil (pt-BR)**.
2. **Auditoria Rigorosa de Licenças (Zero Pirataria):**
   - NUNCA introduzir textos protegidos por copyright moderno (ex: ARA, NVI, NAA, NTLH) em `corpus/approved/` ou no repositório público.
   - Todo arquivo adicionado em `corpus/approved/` DEVE ter sua proveniência comprovada em `corpus/approved/manifest.json` com hash SHA-256 verificado.
   - Materiais com licenças não comerciais (CC BY-NC) ou share-alike (CC BY-SA) devem ser claramente segregados ou mantidos em quarentena local (`corpus/quarantine/`).
3. **Engenharia Cirúrgica e Autossuficiente:**
   - O projeto utiliza a biblioteca padrão do Python (`sqlite3` com suporte a FTS5 nativo, `hashlib`, `json`, `argparse`).
   - Gerenciamento de ambiente exclusivamente via `uv`. Nunca executar `pip install` solto.
4. **Isolamento de Clones Upstream:**
   - Todos os clones de repositórios upstream residem em `data/sources/` e são **estritamente ignorados pelo Git**.
   - NUNCA submeter commits contendo pastas `.git` aninhadas de terceiros.

---

## 2. Comandos do CLI (`bref`)

O CLI da biblioteca é invocado por `python -m biblioteca_reformada.cli` ou pelo atalho `bref`:

- `bref audit`: Valida integridade SHA-256 e conformidade jurídica do corpus.
- `bref sync [--dry-run] [--fetch]`: Sincroniza e clona repositórios upstream de fontes catalogadas.
- `bref import-blivre`: Importa dados canônicos da Bíblia Livre (BLIVRE) para o banco de dados e corpus aprovado.
- `bref index`: Recria ou atualiza a tabela virtual SQLite FTS5 para busca textual ultraveloz.
- `bref search "<termo>"`: Executa consulta FTS5 e retorna referências canônicas exatas (`[Livro C:V] Texto (Versão)`).
- `bref stats`: Exibe estatísticas consolidadas de versículos, livros, autores e matriz de licenças.

---

## 3. Fluxo de Validação Antes de Qualquer Commit

1. Executar os testes automatizados:
   ```powershell
   pytest
   ```
2. Executar auditoria de licenças:
   ```powershell
   python -m biblioteca_reformada.cli audit
   ```
3. Executar consulta de teste:
   ```powershell
   python -m biblioteca_reformada.cli search "verdade"
   ```
