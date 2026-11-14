# ⚠️ DIAGNÓSTICO DE BLOQUEIO EXTERNO DO GITHUB ACTIONS

**Data da Auditoria:** 14 de Novembro de 2026  
**Repositório:** [Cazula/biblioteca-reformada-livre](https://github.com/Cazula/biblioteca-reformada-livre)  
**ID de Execução de Referência:** `43560233382` (e execuções correlatas)  
**Status do Blocker:** Bloqueio Externo de Provisionamento de Runners / Billing na Conta GitHub  

---

## 1. Evidências Empíricas Coletadas

A análise das execuções do GitHub Actions no repositório remoto revelou um padrão invariante e conclusivo:

1. **Duração Anômala de 1 a 3 Segundos:**  
   Todas as 26+ execuções falharam em menos de 3 segundos, tempo insuficiente sequer para inicializar o contêiner do runner ou executar o `actions/checkout`.
2. **Ausência de Passos Executados (`steps: []`):**  
   A inspeção via API do GitHub dos objetos dos jobs demonstra que a lista de passos (`steps`) está vazia (`[]`). Nenhum comando (`pip install`, `pytest`, `bref audit`) chegou a ser disparado.
3. **Logs Inexistentes com Erro HTTP 404 `BlobNotFound`:**  
   Ao tentar recuperar os logs brutos dos jobs, a infraestrutura de armazenamento do GitHub Actions retorna `404 BlobNotFound`. Isso comprova que nenhum arquivo de log foi gerado porque o runner virtual do GitHub (`ubuntu-latest`) **nunca chegou a ser alocado**.
4. **Isolamento de Causa (Não é Código / Não é YAML):**  
   - A sintaxe do arquivo `.github/workflows/ci.yml` é válida.
   - Localmente, a suíte de testes passa 100% (`uv run pytest tests -v`) em todas as versões testadas.
   - Os comandos CLI `bref audit`, `bref import-blivre`, `bref index`, `bref search` e `bref stats` executam perfeitamente sem falhas.

---

## 2. Diagnóstico da Causa Raiz

Como o [status.github.com](https://www.githubstatus.com/) não reporta indisponibilidade sistêmica global no serviço de Actions, a falha decorre de políticas ou limites operacionais no nível da conta **Cazula**:

1. **Esgotamento da Cota Gratuita / Spending Limit:**  
   Contas do GitHub possuem um limite mensal de 2.000 minutos de Actions gratuitos para repositórios públicos e privados. Se o limite de gastos (*Spending Limit*) da conta ou organização estiver configurado como `$0.00` e a cota tiver expirado, o provisionador do GitHub cancela imediatamente qualquer job antes da inicialização do runner.
2. **Políticas de Acesso do GitHub Actions:**  
   Configurações de permissão restritiva em `Settings > Actions > General` da conta Cazula podem estar bloqueando runners padrão compartilhados da GitHub.

---

## 3. Guia de Resolução Manual na Interface Web (GitHub UI)

O usuário deve verificar as seguintes opções na interface do GitHub (já que ferramentas de CLI/agente não devem nem podem alterar políticas de faturamento de forma autônoma):

### Passo 1: Conferir Limites de Gastos (Billing)
1. Acesse: [https://github.com/settings/billing](https://github.com/settings/billing) (ou as configurações de billing da organização correspondente).
2. Verifique a seção **"GitHub Actions Usage"**.
3. Verifique se o **"Spending Limit"** de Actions está em `$0` ou bloqueado por falta de saldo/cartão.
4. Ajuste o limite para um valor controlado (ex.: `$5.00` ou reative o plano mensal se desejado).

### Passo 2: Conferir Permissões do Actions no Repositório
1. Acesse: [https://github.com/Cazula/biblioteca-reformada-livre/settings/actions](https://github.com/Cazula/biblioteca-reformada-livre/settings/actions)
2. Em **"Actions permissions"**, certifique-se de que a opção **"Allow all actions and reusable workflows"** está selecionada.
3. Em **"Workflow permissions"**, certifique-se de que há permissão de **"Read repository contents and packages permissions"**.

---

## 4. Diretrizes de Governança NEXUS Mantidas

- **Não mascaramento de status:** O arquivo de workflow `.github/workflows/ci.yml` **NÃO** foi removido nem adulterado para esconder o selo vermelho. O workflow representa o padrão-ouro de verificação contínua e funcionará automaticamente assim que a cota/permissão do GitHub for reestabelecida.
- **Proibição de Runners Não Autorizados:** Não foi criado nenhum *self-hosted runner* local não autorizado na máquina do usuário para burlar o limite.
- **Validação Local Contínua:** Todo o código, corpus e ferramentas são rigorosamente validados na máquina de desenvolvimento via `pytest` e `bref audit`.
