<template>
  <div>
    <div class="filtros">
      <input v-model="busca" placeholder="Buscar por título..." @input="carregar" />
      <select v-model="statusFiltro" @change="carregar">
        <option value="">Todos os status</option>
        <option value="aberta">Aberta</option>
        <option value="em_andamento">Em andamento</option>
        <option value="concluida">Concluída</option>
        <option value="cancelada">Cancelada</option>
      </select>
      <select v-model="prioridadeFiltro" @change="carregar">
        <option value="">Todas as prioridades</option>
        <option value="baixa">Baixa</option>
        <option value="media">Média</option>
        <option value="alta">Alta</option>
      </select>
      <router-link to="/solicitacoes/novo" class="botao">+ Nova</router-link>
    </div>

    <p v-if="erro" class="erro">{{ erro }}</p>

    <table v-if="solicitacoes.length">
      <thead>
        <tr>
          <th>Título</th>
          <th>Status</th>
          <th>Prioridade</th>
          <th>Autor</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="s in solicitacoes" :key="s.id" @click="abrir(s.id)">
          <td>{{ s.titulo }}</td>
          <td>{{ s.status }}</td>
          <td>{{ s.prioridade }}</td>
          <td>{{ s.autor_nome }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else>Nenhuma solicitação encontrada.</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api.js'

const solicitacoes = ref([])
const busca = ref('')
const statusFiltro = ref('')
const prioridadeFiltro = ref('')
const erro = ref('')
const router = useRouter()

async function carregar() {
  erro.value = ''
  try {
    const response = await api.get('/solicitacoes/', {
      params: {
        // O backend usa SearchFilter (search_fields = ['titulo']), cujo
        // parâmetro padrão é "search"; status e prioridade vêm do FilterSet.
        search: busca.value || undefined,
        status: statusFiltro.value || undefined,
        prioridade: prioridadeFiltro.value || undefined,
      },
    })
    solicitacoes.value = response.data
  } catch (e) {
    erro.value = 'Não foi possível carregar as solicitações.'
  }
}

function abrir(id) {
  router.push(`/solicitacoes/${id}`)
}

onMounted(carregar)
</script>

<style scoped>
.filtros { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
.filtros input, .filtros select { padding: 0.4rem; }
.botao { margin-left: auto; background: #1f2937; color: white; padding: 0.4rem 0.8rem; border-radius: 4px; text-decoration: none; }
table { width: 100%; border-collapse: collapse; background: white; }
th, td { text-align: left; padding: 0.6rem; border-bottom: 1px solid #e5e7eb; }
tbody tr { cursor: pointer; }
tbody tr:hover { background: #f3f4f6; }
.erro { color: #b91c1c; }
</style>
