import { createRouter, createWebHistory } from 'vue-router'
import Login from './views/Login.vue'
import Lista from './views/Lista.vue'
import Detalhe from './views/Detalhe.vue'

const routes = [
  { path: '/login', name: 'login', component: Login },
  { path: '/', name: 'lista', component: Lista, meta: { requiresAuth: true } },
  { path: '/solicitacoes/:id', name: 'detalhe', component: Detalhe, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Guard global: bloqueia rotas protegidas para usuários não autenticados e
// evita que um usuário já logado volte para a tela de login.
router.beforeEach((to) => {
  const autenticado = !!localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !autenticado) {
    return { name: 'login' }
  }
  if (to.name === 'login' && autenticado) {
    return { name: 'lista' }
  }
})

export default router
