# Desafio Técnico — Revisão de Código e Correção de Problemas

**Prazo de entrega:** 2 dias corridos a partir do recebimento
**Formato de entrega:** fork ou branch neste repositório, com suas alterações, PR/MR aberto contra a branch principal (ou instruções equivalentes se preferir enviar de outra forma)

---

## 1. Contexto

Este repositório contém um mini-sistema de **gestão de solicitações internas** (Vue.js + Django REST + PostgreSQL), similar a um módulo real que está em manutenção pelo time.

O sistema **já funciona** — sobe com Docker, tem autenticação, listagem, criação e edição de solicitações. Só que, como em qualquer código real herdado, ele tem problemas: bugs, más práticas e implementações incompletas de regras de negócio que deveriam existir.

Este desafio simula uma tarefa comum do dia a dia: **entrar em um código que você não escreveu, entender o que ele faz, identificar problemas e corrigi-los.**

---

## 2. O que você precisa fazer

1. Subir o projeto localmente (`docker-compose up --build`).
2. Explorar a aplicação e o código (frontend e backend).
3. Rodar os testes automatizados já existentes no backend (`docker-compose exec backend python manage.py test`) — alguns **vão falhar de propósito**. Cada teste que falha descreve, no próprio nome/docstring, uma regra de negócio que deveria estar correta e não está.
4. Corrigir os problemas até que os testes passem — e, além dos testes, revisar o restante do código (frontend incluso) em busca de outros problemas que não estão cobertos por teste automatizado.
5. Documentar o que você encontrou e corrigiu.

Você **não precisa** adivinhar problemas aleatórios: os testes que falham são o ponto de partida oficial. Mas fique atento — nem todo problema do repositório está coberto por um teste.

---

## 3. Regras de negócio esperadas (para referência)

Estas são as regras que o sistema **deveria** seguir. Use-as como critério ao revisar o código:

1. Um usuário só pode editar ou excluir suas próprias solicitações.
2. Exclusão de solicitação deve ser soft delete (não remover do banco).
3. Não deve ser possível pular etapas do fluxo de status sem justificativa — especificamente, não é permitido ir de `concluida` direto para `aberta`.
4. A listagem deve suportar filtro por status, prioridade e busca por texto no título, e esses filtros devem realmente funcionar quando usados na interface.
5. Autenticação deve proteger tanto a API quanto as rotas do frontend — um usuário deslogado não deveria conseguir ver a listagem só por digitar a URL.
6. Título da solicitação não pode ser salvo vazio ou só com espaços.

---

## 4. O que entregar

No seu fork/branch, inclua um `RELATORIO.md` (ou seção no README) descrevendo:

1. **Lista dos problemas encontrados** — um por um, com:
   - Onde estava (arquivo/linha ou trecho).
   - Por que era um problema (impacto real: segurança, dado incorreto, UX quebrada, etc.).
   - Como você corrigiu.
2. Quais problemas vieram dos testes que falhavam vs. quais você encontrou por conta própria revisando o código.
3. Se sobrou tempo, o que mais você melhoraria no projeto (mesmo sem implementar).
4. Seção `## Uso de IA`: onde ferramentas de IA te ajudaram a encontrar ou corrigir os problemas, e onde você precisou revisar/discordar de uma sugestão.

---

## 5. Requisitos técnicos

- Toda correção no backend deve manter (ou adicionar) cobertura de teste correspondente.
- Correções no frontend devem ser verificáveis manualmente (descreva no relatório como testar cada uma).
- Não é necessário adicionar funcionalidades novas além de corrigir o que já existe — o foco é qualidade da correção, não escopo novo.
- Mantenha o histórico de commits organizado: prefira um commit por problema corrigido a um único commit gigante no final.

---

## 6. Como rodar o projeto

```bash
docker-compose up --build
```

- Backend: `http://localhost:8000/api/`
- Frontend: `http://localhost:5173`
- Admin do Django: `http://localhost:8000/admin/`

**Usuários de teste (já no seed):**

| Usuário | Senha    |
|---------|----------|
| ana     | senha123 |
| bruno   | senha123 |
| admin   | admin123 (superusuário) |

Para rodar os testes do backend:

```bash
docker-compose exec backend python manage.py test
```

---

## 7. Critérios de avaliação

- **Capacidade de diagnóstico**: você entendeu corretamente a causa raiz de cada problema, ou só tratou o sintoma?
- **Qualidade da correção**: a solução é robusta ou só faz o teste passar de forma frágil?
- **Cobertura de testes**: você manteve/ampliou os testes de forma coerente?
- **Comunicação**: o relatório explica claramente o raciocínio, para que outra pessoa do time entenda o que mudou e por quê.
- **Priorização**: dado o prazo curto, você tratou os problemas de maior impacto primeiro (ex: segurança/permissão antes de um filtro de UI)?
- **Uso de IA**: como ferramentas de IA foram usadas de forma crítica no processo.

> Não esperamos que todos os problemas sejam encontrados e corrigidos em 2 dias. Preferimos ver poucos problemas bem diagnosticados e bem corrigidos, com raciocínio claro, do que muitos remendados às pressas.

---

## 8. Dúvidas

Se encontrar algo ambíguo sobre o comportamento esperado, documente a premissa assumida no relatório e siga em frente.
