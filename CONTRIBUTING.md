# Guia de Contribuição — Biblioteca Reformada Livre

Agradecemos o interesse em contribuir com a **Biblioteca Reformada Livre**! Este projeto é dedicado a disponibilizar textos bíblicos, teologia reformada clássica, confissões e ferramentas de exegese sob padrões rigorosos de integridade e conformidade de licenças.

---

## Como Contribuir

1. **Adição de Novas Obras:**
   - Verifique a licença da obra proposta antes de submeter qualquer PR.
   - Obras devem estar em Domínio Público comprovado ou sob licenças abertas permissivas (CC0, CC BY 3.0/4.0).
   - Cadastre a nova fonte em `catalog/sources.json`.
   - Adicione o manifesto com hash SHA-256 em `corpus/approved/manifest.json`.

2. **Melhorias de Código e Ferramentas:**
   - O código deve manter 100% de compatibilidade com Python 3.10+ sem dependências externas obrigatórias além da biblioteca padrão.
   - Adicione testes unitários em `tests/` para qualquer nova funcionalidade.
   - Garanta que `pytest` e `python -m biblioteca_reformada.cli audit` passem com sucesso.

3. **Padrão de Código:**
   - Docstrings e comentários em Português do Brasil (pt-BR).
   - Tipagem com Type Hints do Python (`typing` / `dataclasses`).
   - Tratamento explícito de exceções e codificação UTF-8 obrigatória.
