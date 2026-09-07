# Relatório — Desafio de Revisão de Código

## Resumo

Subi o projeto com Docker, rodei os testes do backend (3 falhavam de propósito) e
corrigi as três regras quebradas. Em seguida revisei o restante do código —
backend e frontend — e encontrei mais quatro problemas que não estavam cobertos
por teste (validação de título, autenticação no frontend, filtro de busca e um
N+1 de performance).

Ao final: **backend com 9 testes verdes** (os 3 originais + 6 que adicionei) e as
correções de frontend verificadas manualmente no navegador.

Priorizei por impacto: primeiro segurança e integridade de dados
(permissão, soft delete, transição de status, autenticação), depois UX e
performance (filtro de busca, N+1).

## Como validar

```bash
docker compose up --build -d
docker compose exec backend python manage.py test   # deve dar 9 OK
```

Frontend em `http://localhost:5173` (login `ana` / `senha123`). Os passos de
verificação manual de cada correção de frontend estão descritos abaixo.

---

## Problemas que vinham dos testes que falhavam

### 1. Um usuário conseguia editar/excluir solicitações de outro (segurança)

- **Onde:** `backend/solicitacoes/views.py` — a viewset usava apenas
  `permission_classes = [IsAuthenticated]`.
- **Por que era problema:** isso só verifica se a pessoa está logada. Qualquer
  usuário autenticado podia editar ou excluir a solicitação de qualquer outro
  (o `PATCH` de terceiros retornava `200`). É uma falha de autorização.
- **Como corrigi:** criei a permissão `IsAutorOrReadOnly`
  (`backend/solicitacoes/permissions.py`) — leitura liberada para qualquer
  autenticado, mas edição/exclusão apenas para o autor — e apliquei na viewset.
- **Teste:** `test_usuario_nao_pode_editar_solicitacao_de_outro` (passou a
  retornar `403`).

### 2. Exclusão apagava do banco em vez de ser soft delete

- **Onde:** `backend/solicitacoes/views.py` — `perform_destroy` chamava
  `instance.delete()`.
- **Por que era problema:** removia o registro definitivamente, perdendo
  histórico e auditoria de forma irreversível.
- **Como corrigi:** adicionei o campo `excluido_em` (`models.py` + migration
  `0002`). O `perform_destroy` agora marca a data de exclusão, e a queryset da
  API filtra as excluídas (`excluido_em__isnull=True`). O registro permanece
  no banco, mas some das consultas.
- **Diagnóstico que vale destacar:** o teste verifica a existência do registro
  usando o *manager padrão* (`Solicitacao.objects.filter(...).exists()`). Por
  isso **não** escondi os excluídos no manager (padrão comum), e sim na view —
  assim o registro continua no banco (passa o teste) e ainda some da listagem
  (regra de UX).
- **Testes:** `test_delete_deve_ser_soft_delete` +
  `test_solicitacao_excluida_nao_aparece_na_listagem` (adicionado por mim, cobre
  a outra metade da regra).

### 3. Era possível reabrir uma solicitação concluída direto para "aberta"

- **Onde:** `backend/solicitacoes/serializers.py` — não havia validação de
  transição de status.
- **Por que era problema:** qualquer mudança de status era aceita, permitindo
  pular etapas do fluxo e deixar o dado inconsistente.
- **Como corrigi:** adicionei `validate()` no `SolicitacaoSerializer` comparando
  o status atual (`self.instance`) com o novo; a transição `concluida → aberta`
  passa a retornar `400`. Transições válidas continuam funcionando.
- **Testes:** `test_nao_permite_reabrir_solicitacao_concluida_diretamente` +
  `test_permite_transicao_de_status_valida` (adicionado por mim, garante que não
  bloqueei transições legítimas por engano).

---

## Problemas que encontrei revisando o código (sem teste)

### 4. Título podia ser salvo vazio ou só com espaços

- **Onde:** `backend/solicitacoes/serializers.py`.
- **Por que era problema:** o `CharField` já barra `""`, mas aceita `"   "`
  (só espaços), violando a regra 6 e gerando dados sujos.
- **Como corrigi:** `validate_titulo` faz `strip()`, rejeita se ficar vazio
  (`400`) e normaliza removendo espaços das pontas antes de salvar.
- **Teste:** `test_nao_permite_titulo_em_branco` (adicionado por mim).

### 5. Autenticação não protegia nem a API nem as rotas do frontend

- **Onde:** `frontend/src/services/api.js` e `frontend/src/router.js`.
- **Por que era problema:** dois furos que compõem a regra 5:
  1. O token era salvo no login, mas **nunca enviado** nas requisições. Como a
     API só aceita JWT, toda chamada voltava `401` — na prática a listagem nem
     carregava depois do login.
  2. Não havia guard de rota: um usuário deslogado acessava `/` e
     `/solicitacoes/:id` só digitando a URL.
- **Como corrigi:**
  - `api.js`: interceptor de *request* anexa `Authorization: Bearer <token>`;
    interceptor de *response* limpa a sessão e redireciona ao login em `401`.
  - `router.js`: guard `beforeEach` bloqueia rotas com `meta.requiresAuth` para
    não autenticados (e tira o usuário já logado da tela de login).
- **Como testar (manual):** deslogado, acessar `/` → cai no login; logar
  `ana`/`senha123` → a listagem carrega; apagar `access_token` do `localStorage`
  e recarregar → volta ao login.

### 6. Filtro de busca por título não funcionava

- **Onde:** `frontend/src/views/Lista.vue`.
- **Por que era problema:** o campo enviava o parâmetro `titulo`, que a API
  ignora. O `SearchFilter` do DRF espera `search` — então digitar no campo não
  filtrava nada.
- **Como corrigi:** troquei o parâmetro `titulo` por `search`.
- **Como testar (manual):** buscar por "senha" → a lista mostra só "Reset de
  senha do VPN". (Confirmado direto na API: `?search=senha` → 1 resultado;
  `?titulo=senha` → 3, ou seja, era ignorado.)

### 7. N+1 de queries ao serializar o autor (performance)

- **Onde:** `backend/solicitacoes/serializers.py` (o `ComentarioSerializer`
  fazia `User.objects.get(...)` por comentário) e a listagem
  (`autor_nome` acessava `autor.username` por linha).
- **Por que era problema:** uma query por comentário/linha. Escala mal — quanto
  mais registros, mais lento.
- **Como corrigi:** troquei o `SerializerMethodField` por
  `source='autor.username'`; na view usei `select_related('autor')` na listagem
  e `prefetch_related('comentarios__autor')` no detalhe, deixando o número de
  queries constante.
- **Teste:** `test_detalhe_nao_faz_query_por_comentario` — garante que o total
  de queries do detalhe não cresce com a quantidade de comentários.

### Ajuste de infra (pré-requisito para rodar)

O `docker-compose.yml` estava inválido (o `command:` do backend e o `volumes:`
do frontend estavam vazios), e o projeto **não subia**. Corrigi para conseguir
rodar e, de passagem, deixei o guia de execução do `README` mais claro.

---

## Origem de cada problema

| Vieram dos testes que falhavam | Encontrei revisando o código |
|--------------------------------|------------------------------|
| 1. Permissão de edição/exclusão | 4. Título vazio/só espaços |
| 2. Soft delete | 5. Autenticação no frontend |
| 3. Transição de status | 6. Filtro de busca |
| | 7. N+1 de performance |
| | + `docker-compose` inválido (impedia subir) |

---

## O que eu melhoraria se tivesse mais tempo (não implementei)

- **Fluxo de "Nova solicitação":** o link "+ Nova" aponta para
  `/solicitacoes/novo`, que casa com a rota `/solicitacoes/:id` e tenta abrir uma
  solicitação de id "novo". Não existe uma tela de criação — o cadastro pelo
  frontend está incompleto. Não implementei porque seria funcionalidade nova,
  fora do escopo do desafio, mas registro como pendência.
- **Debounce na busca:** hoje a listagem chama a API a cada tecla, sem debounce
  nem cancelamento da requisição anterior; com digitação rápida as respostas
  podem chegar fora de ordem. Um debounce + cancelamento resolveria.
- **Máquina de estados de status completa:** hoje bloqueio só
  `concluida → aberta`; o ideal seria declarar todas as transições válidas em um
  único lugar.
- **Renovação de token:** o `refresh_token` já é salvo no login, mas não é usado
  para renovar o `access` expirado. Dá para automatizar isso no interceptor.
- **Paginação:** a listagem retorna todos os registros de uma vez.
- **Testes de frontend** (Vitest/Cypress) para cobrir guard, interceptor e filtro.

## Nota sobre o ambiente (Windows + Docker)

O HMR do Vite não recarrega de forma confiável sobre *bind mount* no Windows (o
`mtime` nem sempre muda, e o Vite serve código em cache). Para ver alterações de
frontend com segurança, reiniciei o container: `docker compose restart frontend`.
Não é bug do código, mas atrapalhou a verificação até eu identificar a causa.

---

## Uso de IA

Usei o Claude (via Claude Code) como par ao longo de todo o desafio: para subir o
projeto, rodar os testes, investigar a causa raiz de cada problema, implementar as
correções e verificá-las — inclusive dirigindo um navegador para testar o
frontend (login, guard de rota e filtro de busca).

Onde apliquei meu próprio julgamento e revisei/ajustei as sugestões:

- **Estratégia de git:** decidi a estrutura (manter a `main` com o código
  original intocado, uma branch de correções e **um commit por problema**), em
  vez de um commit único no final.
- **Design do soft delete:** validei a decisão de filtrar os excluídos na *view*
  e não no manager padrão — foi o que fez sentido ao ler o que o teste realmente
  verifica (existência via manager padrão). Aceitar a abordagem "esconder no
  manager" teria feito o teste falhar.
- **Escopo:** decidi **não** implementar a tela de "Nova solicitação" (seria
  feature nova) e **não** reescrever o enunciado do `README` do desafio, apenas
  melhorar a seção de execução.
- **Ceticismo na verificação:** quando o filtro de busca parecia não funcionar,
  não aceitei "o código está certo" de imediato — investiguei até concluir que o
  problema era o cache do Vite no Windows, e não a correção.
- **Cobertura de testes:** além de corrigir, adicionei testes para as regras que
  não tinham (título em branco, soft delete some da listagem, transição válida,
  ausência de N+1), para deixar as correções protegidas contra regressão.
