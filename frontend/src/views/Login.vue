<template>
  <div class="login-box">
    <h2>Entrar</h2>
    <form @submit.prevent="entrar">
      <label>Usuário</label>
      <input v-model="username" type="text" required />
      <label>Senha</label>
      <input v-model="password" type="password" required />
      <button type="submit">Entrar</button>
      <p v-if="erro" class="erro">{{ erro }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api.js'

const username = ref('')
const password = ref('')
const erro = ref('')
const router = useRouter()

async function entrar() {
  erro.value = ''
  try {
    const response = await api.post('/token/', {
      username: username.value,
      password: password.value,
    })
    localStorage.setItem('access_token', response.data.access)
    localStorage.setItem('refresh_token', response.data.refresh)
    router.push('/')
  } catch (e) {
    erro.value = 'Usuário ou senha inválidos.'
  }
}
</script>

<style scoped>
.login-box { max-width: 320px; margin: 4rem auto; background: white; padding: 2rem; border-radius: 8px; }
form { display: flex; flex-direction: column; gap: 0.5rem; }
input { padding: 0.5rem; }
button { margin-top: 1rem; padding: 0.6rem; background: #1f2937; color: white; border: none; border-radius: 4px; cursor: pointer; }
.erro { color: #b91c1c; }
</style>
