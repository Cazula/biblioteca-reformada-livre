# 📋 MATRIZ DE GOVERNANÇA E AUDITORIA DE INCLUSÃO (QA-INCLUSION)

**Versão da Matriz:** 1.0.0  
**Data:** 14 de Novembro de 2026  
**Repositório:** [Cazula/biblioteca-reformada-livre](https://github.com/Cazula/biblioteca-reformada-livre)  
**Política Normativa:** `docs/legal/AUDIT_POLICY.md` e `docs/legal/LICENSES.md`  

---

## 1. Visão Geral da Política de Inclusão ("Colocar Dentro")

Nenhuma obra entra no corpus aprovado (`corpus/approved/`) sem atender rigorosamente aos 5 critérios fundamentais:

1. **Licença Permissiva Compatível:** Deve pertencer a `ALLOWED_DISTRIBUTION_LICENSES` (`Public Domain`, `CC0-1.0`, `CC-BY-3.0-BR`, `CC-BY-4.0`, `MIT`, `Apache-2.0`). Obras com restrição Não Comercial (`NC`), sem licença explícita ou com licenças copyleft virais incompatíveis (`GPLv3` para dados) são **retidas em quarentena técnica** e mantidas apenas como referência local.
2. **Edição-Fonte Primária e Proveniência Verificável:** Identificação exata da edição histórica, digitalizador confiável (Gutenberg, CCEL, BLIVRE) e URL segura (`https://`).
3. **Classificação Editorial Honesta (Completude e Tipo de Texto):**
   - `completeness`: `full` (integral) ou `excerpt` (extrato/seleção).
   - `text_type`: `original` (idioma original do autor), `translation` (tradução integral) ou `paraphrase` (extrato/síntese doutrinária).
   - **Regra Anti-Falsificação de Domínio Público:** Traduções ou paráfrases modernas para o português de obras históricas (Lutero 1529, Edwards 1741, 39 Artigos 1571, Confissão 1689) **NÃO herdam o Domínio Público do original** e são licenciadas de forma transparente sob `CC-BY-4.0`, com `human_reviewed: false` e nota explícita de que se tratam de extratos seletivos.
4. **Integridade Criptográfica (SHA-256):** Toda obra aprovada tem seu hash SHA-256 computado e registrado no `corpus/approved/manifest.json`.
5. **Preservação de Versões e Imutabilidade:** Obras aprovadas não sofrem sobrescrita destrutiva silenciosa.

---

## 2. Matriz Obra por Obra do Acervo Teológico

| Identificador (work_id) | Autor e Datas | Título da Obra | Fonte Primária / Edição de Origem | Licença do Original | Licença da Tradução/Extrato | Tipo de Texto | Completude | Hash SHA-256 (no Corpus) | Status de Inclusão | Justificativa / Parecer Editorial |
|---|---|---|---|---|---|---|---|---|---|---|
| `athanasius:incarnation` | Santo Atanásio de Alexandria (c. 296–373) | Da Encarnação do Verbo de Deus | CCEL / Edição de Archibald Robertson (1892, Domínio Público) | Domínio Público universal | `CC-BY-4.0` (Dataset NEUU) | `translation` | `full` (57 capítulos) | `efb5e1a5dde20004fe97ca5a653cdaffc70b55297165297b3cde94a081cdce25` | **APPROVED** | Clássico patrístico cristológico integral. Tradução em 3 passes com glossário teológico auditada pelo NEUU sob CC BY 4.0. |
| `anselm:meditations` | Santo Anselmo de Cantuária (1033–1109) | Orações e Meditações | Christian Classics Ethereal Library (CCEL, Domínio Público) | Domínio Público universal | `CC-BY-4.0` (Dataset NEUU) | `translation` | `full` (24 orações/meditações) | `5985daa4c87b521914e72e397de3efebaa9cb43964e0d8afa5eff9c0f8c84a01` | **APPROVED** | Clássico medieval fundacional sobre o Redentor. Texto integral traduzido e estruturado sob CC BY 4.0. |
| `kempis:imitation` | Tomás de Kempis (1380–1471) | A Imitação de Cristo (Livro 1) | CCEL / Edição de 1418–1427 em Domínio Público universal | Domínio Público universal | `CC-BY-4.0` (Dataset NEUU) | `translation` | `full` (Livro 1 integral, 25 cap.) | `48526c110ef844224dc51476d4817fc3dac04e81f9b059f011afd34b3c0624b2` | **APPROVED** | Obra clássica da *Devotio Moderna*. Livro 1 completo com 954 parágrafos estruturados no FTS5 sob CC BY 4.0. |
| `lawrence:practice` | Irmão Lawrence (1614–1691) | A Prática da Presença de Deus | Edição de Paris (1692, Domínio Público universal) / CCEL | Domínio Público universal | `CC-BY-4.0` (Dataset NEUU) | `translation` | `full` (4 conversas + 15 cartas) | `f62a412df86730b8b1879207bcc903cb15ae496b1b72215a6894e97cc0714b43` | **APPROVED** | Clássico devocional prático integral. Tradução estruturada em 179 parágrafos no FTS5 sob CC BY 4.0. |
| `edwards:sinners-in-the-hands-of-an-angry-god` | Jonathan Edwards (1703–1758) | Pecadores nas Mãos de um Deus Irado | Boston: S. Kneeland & T. Green (1741, Domínio Público); Gutenberg #34632 | Domínio Público universal | `CC-BY-4.0` | `paraphrase` | `excerpt` (20 parágrafos selecionados) | `d9d730980ff5c50080bca589761534170435198848e347879b4b1ff5abe69a0c` | **APPROVED-EXCERPT** | Extrato doutrinário representativo. Honestamente classificado como paráfrase/extrato pedagógico para pesquisa; não alega Domínio Público da tradução moderna. |
| `luther:small-catechism` | Martinho Lutero (1483–1546) | O Catecismo Menor | Wittenberg (1529); Livro de Concórdia (1580, Domínio Público); Gutenberg #16012 | Domínio Público universal | `CC-BY-4.0` | `paraphrase` | `excerpt` (31 seções selecionadas) | `b7ca1974430e2652dd5dc00980036684e30f25ddbd7420b30fa66f7cea3f4937` | **APPROVED-EXCERPT** | Seleção pedagógica das seções centrais do Catecismo Menor (Decálogo, Credo, Oração Dominical, Sacramentos). Rotulado como extrato. |
| `anglican:thirty-nine-articles` | Igreja da Inglaterra (1571) | Os Trinta e Nove Artigos de Religião | Book of Common Prayer (1571/1662, Domínio Público universal) | Domínio Público universal | `CC-BY-4.0` | `paraphrase` | `excerpt` (19 artigos fundamentais) | `b8089b443340d3f2232c7ecc99eb835cb960b05c08afe5ff56ec41378659f2f4` | **APPROVED-EXCERPT** | Extrato representativo de 19 dos 39 Artigos históricos. Não substitui a totalidade dos 39 artigos; classificado como paráfrase/extrato. |
| `baptist:confession-1689` | Batistas Particulares (1689) | A Confissão de Fé Batista de 1689 | Edição original de Londres (1689, Domínio Público universal) | Domínio Público universal | `CC-BY-4.0` | `paraphrase` | `excerpt` (4 capítulos selecionados) | `d8e5fad5be04e2f87144ccec64df078d1e021c10652ac0bfaf76ed5b8fcb9568` | **APPROVED-EXCERPT** | Extrato representativo dos capítulos 1 (Escritura), 2 (Trindade), 3 (Decreto) e 4 (Igreja/Sacramentos). |
| `calvin:institutes-allen-1816` | João Calvino / Trad. John Allen (1771–1839) | Institutas da Religião Cristã (Vol. 1 de 2) | London: J. Walker (1813/1816); Presbyterian Board; Gutenberg eBook #45001 | Domínio Público universal | Domínio Público universal (tradução de 1813/1816) | `translation` | `full` (Volume 1 integral) | *(Pendente ingestão estruturada)* | **CANDIDATE** | Obra magna da Teologia Reformada. Tradução inglesa histórica de John Allen comprovadamente em Domínio Público universal. Aguarda esteira de parsing JSON. |
| `bunyan:pilgrims-progress-1678` | John Bunyan (1628–1688) | O Peregrino (The Pilgrim's Progress) | Londres por Nathaniel Ponder (1678); Projeto Gutenberg eBook #131 | Domínio Público universal | N/A (texto original em inglês) | `original` | `full` (Texto integral histórico) | *(Pendente ingestão estruturada)* | **CANDIDATE** | Maior clássico puritano alegórico. Texto original em inglês em Domínio Público universal indiscutível (> 300 anos). Aguarda ingestão em JSON. |
| `westminster:cfw-abel` | Assembleia de Westminster | Confissão de Fé de Westminster | Edição de 1646; Tradução para português por Abel Santos | Domínio Público universal | `CC-BY-NC-SA-4.0` | `translation` | `full` | N/A (retida localmente) | **REJECTED (QUARANTINE)** | **Rejeitada para distribuição pública:** tradução sob licença Não Comercial (`NC`). Mantida apenas em catálogo local para estudo privado. |
| `hodge:commentary-wcf` | A. A. Hodge (1823–1886) | Comentário sobre a Confissão de Westminster | Edição de 1869; Tradução por Abel Santos | Domínio Público universal | `CC-BY-NC-SA-4.0` | `translation` | `full` | N/A (retida localmente) | **REJECTED (QUARANTINE)** | **Rejeitada para distribuição pública:** licença Não Comercial (`NC`) incompatível com repositório livre permissivo. |
| `calvin:institutas-abel` | João Calvino (1509–1564) | As Institutas da Religião Cristã | Edição de Genebra (1559); Tradução por Abel Santos | Domínio Público universal | `CC-BY-NC-SA-4.0` | `translation` | `full` | N/A (retida localmente) | **REJECTED (QUARANTINE)** | **Rejeitada para distribuição pública:** licença Não Comercial (`NC`). Preservada apenas localmente. |
| `calvin:comentario-efesios-abel` | João Calvino (1509–1564) | Comentário da Epístola aos Efésios | Genebra (1548); Tradução por Abel Santos | Domínio Público universal | `CC-BY-NC-SA-4.0` | `translation` | `full` | N/A (retida localmente) | **REJECTED (QUARANTINE)** | **Rejeitada para distribuição pública:** licença Não Comercial (`NC`). |
| `calvin:comentario-isaias-7-abel` | João Calvino (1509–1564) | Comentário sobre Isaías 7 (Emanuel) | Genebra (1551); Tradução por Abel Santos | Domínio Público universal | `CC-BY-NC-SA-4.0` | `translation` | `full` | N/A (retida localmente) | **REJECTED (QUARANTINE)** | **Rejeitada para distribuição pública:** licença Não Comercial (`NC`). |
| `caryl:exposition-job-abel` | Joseph Caryl (1602–1673) | Exposição Prática sobre o Livro de Jó | Londres (1647–1666); Tradução por Abel Santos | Domínio Público universal | `CC-BY-NC-SA-4.0` | `translation` | `full` | N/A (retida localmente) | **REJECTED (QUARANTINE)** | **Rejeitada para distribuição pública:** licença Não Comercial (`NC`). |
| `westminster:cfw-json-rickserrat` | Assembleia de Westminster | Confissão de Fé de Westminster (JSON) | Repositório GitHub rickserrat | Domínio Público universal | `Unspecified / Quarentena` | `paraphrase` | `full` | N/A (retida localmente) | **REJECTED (QUARANTINE)** | **Rejeitada:** ausência de licença explícita no repositório de origem. |
| `scriptorium:scriptorium-divinum` | Vários Autores Reformados | Acervo Scriptorium Divinum | Repositório scriptorium-divinum | Variada | `Em Auditoria` | `translation` | `abridged` | N/A (retida localmente) | **REJECTED (QUARANTINE)** | **Rejeitada:** clone upstream incompleto e licenças heterogêneas sem auditoria item-a-item. |

---

## 3. Matriz do Acervo Bíblico Aprovado (Bíblia Livre - BLIVRE)

| Coleção Canônica | Livros | Versículos Indexados | Edição de Origem | Licença Declarada | Atribuição Obrigatória | Status |
|---|---|---|---|---|---|---|
| **Antigo Testamento (AT)** | 39 livros (Gênesis a Malaquias) | 23.145 versículos | Projeto Bíblia Livre (BLIVRE) | `CC-BY-3.0-BR` | "Bíblia Livre (BLIVRE) por Diego Santos e colaboradores, CC BY 3.0 BR." | **APPROVED (100%)** |
| **Novo Testamento (NT)** | 27 livros (Mateus a Apocalipse) | 7.955 versículos | Projeto Bíblia Livre (BLIVRE) | `CC-BY-3.0-BR` | "Bíblia Livre (BLIVRE) por Diego Santos e colaboradores, CC BY 3.0 BR." | **APPROVED (100%)** |
| **Total Canônico** | **66 Livros** | **31.100 Versículos** | **Texto integral** | **CC-BY-3.0-BR** | **100% Auditado pelo `manifest.json`** | **APPROVED** |

---

## 4. Sumário Estatístico da Avaliação Editorial

- **Total de Obras Teológicas Catalogadas:** 18
- **Obras Aprovadas Integrais no Corpus:** 4 (`athanasius`, `anselm`, `kempis`, `lawrence`)
- **Obras Aprovadas Extratos Doutrinários no Corpus:** 4 (`edwards`, `luther`, `anglican`, `baptist`)
- **Obras Candidatas Aprovadas para Futura Ingestão:** 2 (`calvin:institutes-allen-1816` e `bunyan:pilgrims-progress-1678`)
- **Obras Retidas em Quarentena / Não Distribuíveis:** 8 (6 sob licença `CC-BY-NC-SA-4.0` e 2 sem licença explícita)
- **Total de Livros Bíblicos Aprovados no Corpus:** 66 livros (31.100 versículos)
- **Total Geral de Arquivos no Manifesto Aprovado:** **74 arquivos**
- **Taxa de Conformidade Criptográfica em Clone Limpo:** **100% (0 divergências, 0 arquivos órfãos)**

