import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
})

// Anexa o token JWT (salvo no login) em todas as requisições.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Se a API responder 401 (token ausente ou expirado), limpa a sessão e
// redireciona para a tela de login.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

export default api
