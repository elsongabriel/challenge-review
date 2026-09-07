import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
})

// NOTE: o token é salvo no localStorage no momento do login (ver Login.vue),
// mas não há nenhum interceptor aqui garantindo que ele seja enviado em
// TODAS as requisições subsequentes. Vale revisar se isso é suficiente.

export default api
