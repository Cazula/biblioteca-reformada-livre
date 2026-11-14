# Política de Proveniência e Auditoria Criptográfica de Fontes

A **Biblioteca Reformada Livre** adota uma política rigorosa de rastreabilidade para garantir integridade teológica, fidelidade textual e conformidade jurídica.

---

## 1. Princípios de Proveniência

1. **Rastreabilidade de Origem:**
   Toda obra incorporada ao diretório `corpus/approved/` deve registrar:
   - Identificador único da obra (`id`)
   - Título e subtítulo
   - Autor ou tradutor original
   - URL do repositório upstream ou fonte primária
   - Hash SHA-256 do arquivo original e do arquivo normalizado
   - Licença jurídica comprovada
   - Data da extração e responsável pela auditoria

2. **Imutabilidade e Verificação Criptográfica:**
   O arquivo `corpus/approved/manifest.json` atua como cartório digital do repositório. O comando `bref audit` recalcula em tempo real o hash SHA-256 de cada arquivo e compara com o manifesto. Qualquer divergência bloqueia o build e o pipeline de CI.

3. **Separação Rígida de Camadas:**
   - `data/sources/`: Clones brutos locais (gitignored, rasos via `--depth 1`, nunca enviados para repositórios remotos).
   - `corpus/quarantine/`: Dados sob investigação de licença ou aguardando resolução jurídica (gitignored).
   - `corpus/approved/`: Arquivos normalizados, auditados juridicamente, validados criptograficamente e versionados.
