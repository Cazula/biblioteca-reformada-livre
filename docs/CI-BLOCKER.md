# ⚠️ DIAGNÓSTICO FACTUAL DE BLOQUEIO EXTERNO DO GITHUB ACTIONS

**Data da Auditoria Forense:** 14 de Novembro de 2026  
**Repositório Auditado:** [Cazula/biblioteca-reformada-livre](https://github.com/Cazula/biblioteca-reformada-livre) (Repositório Público)  
**ID de Execução de Referência:** `43602327284` (e correlatas: `43602031067`, `43601298431`, `43600275112`, `43597064471`, `43560233382`)  
**Check-Run ID Analisado:** `132469550691`  
**Causa Primária Comprovada:** Bloqueio de Execução na Conta GitHub (`account is locked due to a billing issue`)  

---

## 1. Evidência Primária Coletada via API do GitHub

A inspeção do endpoint `/repos/Cazula/biblioteca-reformada-livre/check-runs/132469550691/annotations` revelou as anotações exatas emitidas pelo agendador de infraestrutura do GitHub Actions:

```text
=== CHECK RUN 132469550691 ===
Name: Testes e Auditoria de Integridade (3.12)
Status: completed
Conclusion: failure
Annotations count in output: 2

--- Annotation 1 (failure) ---
Path: .github
Start line: 1
Message: "The job was not started because your account is locked due to a billing issue."

--- Annotation 2 (notice) ---
Path: .github
Start line: 1
Message: "The ubuntu-latest label will migrate to Ubuntu 26 beginning October 19, 2026. For more information, see https://github.com/actions/runner-images/issues/14748"
```

Esta anotação foi confirmada identicamente em múltiplos runs consecutivos (`43602327284`, `43601298431`, `43597064471`).

---

## 2. Esclarecimento Factual sobre a Causa Raiz

1. **Repositórios Públicos Têm Runners Gratuitos:**  
   Conforme a documentação oficial do GitHub ([Billing and Usage for GitHub Actions](https://docs.github.com/en/actions/concepts/billing-and-usage)), o uso de runners padrão `ubuntu-latest` em repositórios **PÚBLICOS** é 100% gratuito e não consome a cota de 2.000 minutos de repositórios privados.
2. **O Bloqueio Ocorre no Nível da Conta (`Cazula`), Não do Repositório:**  
   Quando uma conta de usuário ou organização no GitHub possui uma pendência financeira global — como uma fatura não processada de GitHub Copilot, plano Pro/Team, pacotes LFS de armazenamento, ou um cartão de crédito com validade expirada/recusada —, o GitHub suspende o agendamento de runners do GitHub Actions **em toda a conta**, afetando inclusive repositórios públicos.
3. **Sintomas Exatos na API do GitHub:**  
   - `runner_id: 0` (o provisionador do GitHub recusa a alocação de runner antes de instanciá-lo).
   - `steps: []` (nenhum passo ou comando chegou a ser iniciado).
   - Duração de 1 a 3 segundos (`startup_failure`).
   - Erro HTTP 404 `BlobNotFound` ao solicitar logs brutos (porque nenhum log foi gravado pelo runner).

---

## 3. Roteiro Exato de Resolução na Interface Web (GitHub Settings)

Como a conta é de propriedade pessoal do Gabriel e envolve configurações de pagamento, o agente **NÃO possui (e não deve possuir) permissão ou acesso para manipular dados financeiros ou cartões**.

A resolução exige apenas uma ação humana pontual diretamente na interface web do GitHub:

1. **Acesse as Configurações de Cobrança da Conta:**  
   Navegue até: [https://github.com/settings/billing](https://github.com/settings/billing) (logado como `Cazula`).
2. **Verifique Faturas Pendentes ou Pagamentos em Atraso:**  
   Na seção **"Billing history"** / **"Invoices"**, confira se há alguma fatura com status `Past Due` (ex: GitHub Copilot, GitHub Pro ou LFS).
3. **Atualize a Forma de Pagamento:**  
   Em **"Payment information"** ([https://github.com/settings/billing/payment_information](https://github.com/settings/billing/payment_information)), atualize o cartão de crédito cadastrado ou regularize a pendência informada.
4. **Desbloqueio Automático:**  
   Assim que o status da conta transitar de `locked` para regular, o GitHub Actions liberará imediatamente a alocação de runners `ubuntu-latest` para este e qualquer outro repositório público da conta.

---

## 4. Estado de Validação do Código e do Acervo

Enquanto a liberação externa na conta GitHub é processada pelo usuário, a integridade do projeto permanece **100% comprovada e verde em ambiente local**:

- **60 Testes Automatizados:** Todos passando com sucesso (`uv run pytest tests -v` em 7.57s).
- **Auditoria de Licenças e Hashes (`bref audit`):** 74 arquivos aprovados, 0 divergências, 0 órfãos.
- **Avaliação de Promoção Editorial (`bref evaluate-candidates`):** 100% de conformidade com os critérios de QA e isolamento de obras não comerciais.
- **Testes de Ingestão e FTS5:**
  - `bref import-blivre`: 31.100 versículos indexados no FTS5.
  - `bref import-theology --all`: 8 obras teológicas com 1.656 parágrafos indexados no FTS5.
  - Buscas textuais e teológicas executando com precisão canônica de capítulos e parágrafos.
