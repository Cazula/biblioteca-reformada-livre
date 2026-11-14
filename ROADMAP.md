# 🗺️ ROADMAP — Biblioteca Reformada Livre

Planejamento estratégico de evolução da infraestrutura, acervo e inteligência teológica da Biblioteca Reformada Livre.

---

## Fase 1: Fundação Canônica & Motor FTS5 (Em Andamento / Entregue)
- [x] Arquitetura de CLI em Python (`bref`) com biblioteca padrão e zero bloat.
- [x] Motor de busca textual em SQLite FTS5 com tabelas virtuais de alta performance.
- [x] Sistema de auditoria de integridade com hashes SHA-256 e manifesto de proveniência.
- [x] Catálogo unificado de fontes (`catalog/sources.json`) com matriz jurídica de licenças.
- [x] Ingestão da Bíblia Livre (BLIVRE) sob licença Creative Commons Atribuição 3.0 Brasil.
- [x] Suíte de testes automatizados com cobertura de CLI, banco de dados e auditoria.
- [x] CI automatizado via GitHub Actions.

---

## Fase 2: Padrões Confessionais & Catecismos Históricos
- [ ] Incorporação auditada dos Três Pontos de Unidade (Confissão Belga, Catecismo de Heidelberg, Cânones de Dort).
- [ ] Padrões de Westminster (Confissão de Fé, Catecismo Maior e Breve Catecismo) com auditoria de tradução em Domínio Público.
- [ ] Tabela de correlação entre artigos confessionais e referências bíblicas de prova.
- [ ] Módulo de busca cruzada: consultar confissões e versículos canônicos na mesma consulta.

---

## Fase 3: RAG Híbrido & Recuperação Semântica Teológica
- [ ] Ingestão de embeddings vetoriais com pgvector ou ChromaDB local.
- [ ] Mecanismo de busca híbrida (FTS5 BM25 + Similaridade Cosseno vetorial).
- [ ] Roteador semântico de perguntas teológicas: conectar dúvidas doutrinárias diretamente a trechos canônicos e confessionais.
- [ ] Operação offline com modelo local (Qwen 2.5 Coder / Ollama) via NEXUS.

---

## Fase 4: Frontend Web Moderno & Leitor Interativo
- [ ] Interface visual em Astro v5 + Vanilla CSS Tokens (padrão Cazula Design System).
- [ ] Leitor bíblico com busca instantânea em milissegundos (Client-side WASM SQLite ou API local).
- [ ] Visualização paralela: comparação entre traduções bíblicas livres e notas exegéticas.
- [ ] Grafo de referências cruzadas interativo baseado no dataset NEUU.

---

## Fase 5: Esteira de Tradução Auditada & Alinhamento Interlinear
- [ ] Pipeline de extração e alinhamento de textos do Hebraico (Tanakh) e Grego (Textus Receptus / NA28 em Domínio Público).
- [ ] Mapeamento lexico-morfológico com Strong's Concordance em Domínio Público.
- [ ] Fluxo de revisão humana-in-the-loop para propostas de melhoria de tradução.
