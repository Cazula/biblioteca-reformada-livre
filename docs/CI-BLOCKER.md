# ⚠️ DIAGNÓSTICO DE BLOQUEIO EXTERNO DO GITHUB ACTIONS

**Data da Auditoria:** 14 de Novembro de 2026  
**Repositório:** [Cazula/biblioteca-reformada-livre](https://github.com/Cazula/biblioteca-reformada-livre) (Repositório Público)  
**ID de Execução de Referência:** `43560233382` (e execuções correlatas)  
**Classificação Factual do Status:** Causa Indeterminada de Falha Anterior às Etapas (`startup_failure` / falha de alocação de runner)  

---

## 1. Evidências Empíricas Coletadas

A análise das execuções do GitHub Actions no repositório remoto revelou um padrão invariante e comprovado pelos dados da API:

1. **Duração Anômala de 1 a 3 Segundos:**  
   Todas as execuções falharam em menos de 3 segundos, tempo insuficiente sequer para inicializar o contêiner do runner ou executar o `actions/checkout`.
2. **Ausência de Passos Executados (`steps: []`):**  
   A inspeção via API do GitHub dos objetos dos jobs demonstra que a lista de passos (`steps`) está vazia (`[]`). Nenhum comando (`pip install`, `pytest`, `bref audit`) chegou a ser disparado.
3. **Logs Inexistentes com Erro HTTP 404 `BlobNotFound`:**  
   Ao tentar recuperar os logs brutos dos jobs via API, a infraestrutura de armazenamento do GitHub Actions retorna `404 BlobNotFound`. Isso comprova que nenhum arquivo de log foi gerado porque o runner virtual do GitHub (`ubuntu-latest`) **nunca chegou a ser alocado pelo provisionador**.
4. **Isolamento de Causa (Não é Código / Não é YAML):**  
   - A sintaxe do arquivo `.github/workflows/ci.yml` é estritamente válida.
   - Localmente, a suíte de 47 testes automatizados passa 100% (`uv run pytest tests -v`).
   - Os comandos CLI `bref audit`, `bref import-blivre`, `bref index`, `bref search` e `bref stats` executam perfeitamente sem falhas.

---

## 2. Esclarecimento sobre Billing e Causa Raiz

Conforme a documentação oficial do GitHub ([Billing and Usage for GitHub Actions](https://docs.github.com/en/actions/concepts/billing-and-usage) e [GitHub-hosted Runners Overview](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)):
- O uso de runners padrão hospedados pelo GitHub (`ubuntu-latest`) em repositórios **PÚBLICOS** é **gratuito e ilimitado**.
- Portanto, a hipótese anterior de "esgotamento da cota de 2.000 minutos mensais ou spending limit de $0" **NÃO se aplica** e é factualmente improcedente para repositórios públicos.
- A falha deve ser classificada com precisão técnica e factual como: **Causa Indeterminada de Falha Anterior às Etapas (`startup_failure` / falha no provisionamento pré-runner)**.

As causas plausíveis restantes dentro da plataforma GitHub incluem:
1. **Políticas de Acesso do Actions na Conta / Organização:**  
   Configurações em `Settings > Actions > General` que restrinjam a execução de workflows por permissões de repositório, ou exigência de aprovação manual prévia para execuções.
2. **Restrições Temporárias de Provisionamento ou Flag na Conta:**  
   Bloqueios operacionais automáticos no pool de runners padrão para a conta, que demandam análise do painel do GitHub ou abertura de chamado no GitHub Support.

---

## 3. Roteiro de Verificação Recomendado na Interface Web (GitHub UI)

O mantenedor pode verificar as seguintes configurações diretamente na interface web do GitHub:

### Passo 1: Conferir Permissões do Actions no Repositório
1. Acesse: [https://github.com/Cazula/biblioteca-reformada-livre/settings/actions](https://github.com/Cazula/biblioteca-reformada-livre/settings/actions)
2. Em **"Actions permissions"**, certifique-se de que a opção **"Allow all actions and reusable workflows"** está selecionada.
3. Em **"Workflow permissions"**, certifique-se de que a opção **"Read repository contents and packages permissions"** está ativa.
4. Em **"Fork pull request workflows"**, conferir se há restrição ou exigência de aprovação de primeiro commit.

### Passo 2: Conferir Permissões Globais da Conta Cazula
1. Acesse as configurações de conta: [https://github.com/settings/actions](https://github.com/settings/actions)
2. Verifique se o GitHub Actions está habilitado globalmente para todos os repositórios públicos.

### Passo 3: Consultar o GitHub Support (se persistir)
Caso as opções acima estejam corretas e novos runs continuem falhando com `steps: []` e `BlobNotFound`, deve-se abrir um chamado no [GitHub Support](https://support.github.com/) relatando o Job ID `43560233382` com falha imediata de provisionamento em repositório público.

---

## 4. Diretrizes de Governança NEXUS Mantidas

- **Não mascaramento de status:** O arquivo de workflow `.github/workflows/ci.yml` **NÃO** foi removido nem adulterado para esconder o selo vermelho. O workflow representa o padrão de verificação contínua e executará assim que a alocação de runners pelo GitHub for concluída.
- **Proibição de Runners Não Autorizados:** Não foi criado nenhum *self-hosted runner* local não autorizado na máquina do usuário para burlar o ambiente.
- **Validação Local Contínua e Fidedigna:** Todo o código, corpus (74 obras: 66 bíblicas + 8 teológicas) e ferramentas são rigorosamente validados na máquina de desenvolvimento via `pytest` (47 testes verdes) e `bref audit` (74/74 aprovados, 0 divergências).
