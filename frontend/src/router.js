import { createRouter, createWebHistory } from 'vue-router'
import Login from './views/Login.vue'
import Lista from './views/Lista.vue'
import Detalhe from './views/Detalhe.vue'

const routes = [
  { path: '/login', name: 'login', component: Login },
  { path: '/', name: 'lista', component: Lista },
  { path: '/solicitacoes/:id', name: 'detalhe', component: Detalhe },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// NOTE: não há nenhum guard global (router.beforeEach) verificando se o
// usuário está autenticado antes de acessar rotas como "/" ou "/solicitacoes/:id".

export default router
