# Política de Auditoria Textual e Jurídica

## 1. Critérios de Aprovação para Ingestão no Corpus

Para que um texto bíblico ou teológico seja promovido de `data/sources/` para `corpus/approved/`, ele deve satisfazer a todos os 4 critérios:

1. **Licença Permissiva Compatível:**
   - Licenças aceitas: Domínio Público, CC0, CC BY 3.0/4.0, MIT, Apache 2.0.
   - Licenças condicionais: CC BY-SA (admissível com declaração formal de share-alike).
   - Licenças proibidas para distribuição no corpus base: CC BY-NC-ND, CC BY-NC, todos os direitos reservados sem autorização expressa.

2. **Integridade Estrutural:**
   - Texto canônico validado: livros bíblicos com numeração correta de capítulos e versículos.
   - Esquema JSON ou texto canônico normalizado UTF-8 sem BOM.

3. **Validação Criptográfica de SHA-256:**
   - O arquivo deve ter seu hash SHA-256 registrado no manifesto.
   - O comando `bref audit` deve passar com código de saída 0.

4. **Atribuição Transparente:**
   - Citação de tradutores, revisores e instituições mantenedoras no cabeçalho ou metadados de exibição.
