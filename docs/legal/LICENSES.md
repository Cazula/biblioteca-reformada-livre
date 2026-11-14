# Política e Matriz de Licenciamento — Biblioteca Reformada Livre

Este documento estabelece a matriz de direitos autorais, termos de uso e compatibilidade jurídica aplicável a todo o código, corpus bíblico, obras confessionais e comentários teológicos do projeto.

---

## 1. Código-Fonte e Ferramentas (MIT License)

Todo o código da aplicação (CLI, motor de busca SQLite FTS5, pipelines de importação, validadores de integridade e suíte de testes) é distribuído sob a licença **MIT**, permitindo uso livre, integração e extensibilidade.

Consulte o arquivo [LICENSE](../../LICENSE) na raiz do projeto.

---

## 2. Matriz de Licenciamento do Corpus Textual

Cada obra ingerida ou catalogada possui uma licença específica vinculada ao seu arquivo de manifesto (`corpus/approved/manifest.json`):

| Obra / Fonte | Repositório Upstream | Licença Declarada | Status no Repositório | Restrições & Observações |
|---|---|---|---|---|
| **Bíblia Livre (BLIVRE)** | `blivre/BibliaLivre` | Creative Commons Atribuição 3.0 Brasil (CC BY 3.0 BR) | **Aprovado (Corpus Base)** | Exige atribuição explícita a Diego Santos e colaboradores do projeto BibliaLivre. Texto livre para redistribuição. |
| **Bíblia Pública (Euaggelion)** | `Projeto-Euaggelion/biblia.publica` | Mista (Domínio Público / CC BY-SA / CC BY-NC-ND) | **Parcial / Filtrado** | **Excluído:** NT 1819a (CC BY-NC-ND); NVA está sob CC BY-SA (exige share-alike). Ingestão condicionada à auditoria por versão. |
| **Bíblia Conectada** | `alexpiraginet-bot/biblia-conectada` | Código MIT / Dados CC BY-SA | **Sob Auditoria** | Filtrar licenças por fonte antes de publicação pública. |
| **Bíblia Libera** | `biblialibera/biblialibera` | CC BY 4.0 (exceto LXX GPLv3) | **Sob Auditoria** | A Septuaginta (LXX) possui trechos em GPLv3; textos com revisão pendente mantidos em quarentena local. |
| **NEUU Datasets** | `neuu-org/*` | CC BY 4.0 declarada | **Aprovado p/ Referências** | Válido para crossrefs, dicionários, tópicos e gazetteers. **PROIBIDO:** `neuu-org/bible-text-dataset` (contém textos modernos protegidos como ARA, NVI, NAA). |
| **Scriptorium Divinum** | `rilsonjoas/scriptorium-divinum` | Código MIT / Textos CC BY-SA | **Quarentena Local** | Clonado apenas em `data/sources/`. Publicação de textos autorizada somente após validação unitária de proveniência de cada arquivo. |
| **Abel Santos (Traduções)** | `separovichabel/abel-santos` | CC BY-NC-SA 4.0 | **Apenas Local / Não Comercial** | Não integrável em produtos de redistribuição comercial livre devido à cláusula Não Comercial (NC). |
| **Confissão de Fé de Westminster (CFW)** | `rickserrat/cfw` | Sem licença explícita | **Quarentena Local** | Conteúdo retido em quarentena até auditoria de titularidade e atribuição de licença aberta. |
| **IPB / Andrew Jumper / Cultura Cristã / Bucer** | N/A (Acervos Institucionais) | Direitos Reservados | **Metadados e Links Apenas** | Apenas catalogação de referências, metadados bibliográficos e links. Proibida a cópia integral não autorizada. |

---

## 3. Diretriz de Quarentena e Proteção

Arquivos com licenças indefinidas, restritivas (NC/ND) ou sem comprovação formal de domínio público/aberto devem obrigatoriamente residir em `corpus/quarantine/` (ignorado pelo Git).
Nenhum texto protegido é adicionado a `corpus/approved/` ou publicado no GitHub.
