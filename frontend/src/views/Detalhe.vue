<template>
  <div v-if="solicitacao">
    <button class="voltar" @click="$router.push('/')">&larr; Voltar</button>

    <form @submit.prevent="salvar" class="form">
      <label>Título</label>
      <input v-model="solicitacao.titulo" type="text" />

      <label>Descrição</label>
      <textarea v-model="solicitacao.descricao" rows="4"></textarea>

      <label>Status</label>
      <select v-model="solicitacao.status">
        <option value="aberta">Aberta</option>
        <option value="em_andamento">Em andamento</option>
        <option value="concluida">Concluída</option>
        <option value="cancelada">Cancelada</option>
      </select>

      <label>Prioridade</label>
      <select v-model="solicitacao.prioridade">
        <option value="baixa">Baixa</option>
        <option value="media">Média</option>
        <option value="alta">Alta</option>
      </select>

      <div class="acoes">
        <button type="submit">Salvar</button>
        <button type="button" class="perigo" @click="excluir">Excluir</button>
      </div>
      <p v-if="mensagem" :class="erro ? 'erro' : 'sucesso'">{{ mensagem }}</p>
    </form>

    <section class="historico" v-if="solicitacao.historico?.length">
      <h3>Histórico de status</h3>
      <ul>
        <li v-for="h in solicitacao.historico" :key="h.id">
          {{ h.status_anterior }} → {{ h.status_novo }}
        </li>
      </ul>
    </section>

    <section class="comentarios">
      <h3>Comentários</h3>
      <ul>
        <li v-for="c in solicitacao.comentarios" :key="c.id">
          <strong>{{ c.autor_nome }}:</strong> {{ c.texto }}
        </li>
      </ul>
      <form @submit.prevent="comentar" class="form-comentario">
        <input v-model="novoComentario" placeholder="Escreva um comentário..." />
        <button type="submit">Enviar</button>
      </form>
    </section>
  </div>
  <p v-else>Carregando...</p>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api.js'

const route = useRoute()
const router = useRouter()
const solicitacao = ref(null)
const novoComentario = ref('')
const mensagem = ref('')
const erro = ref(false)

async function carregar() {
  const response = await api.get(`/solicitacoes/${route.params.id}/`)
  solicitacao.value = response.data
}

async function salvar() {
  mensagem.value = ''
  erro.value = false
  try {
    await api.patch(`/solicitacoes/${route.params.id}/`, {
      titulo: solicitacao.value.titulo,
      descricao: solicitacao.value.descricao,
      status: solicitacao.value.status,
      prioridade: solicitacao.value.prioridade,
    })
    mensagem.value = 'Salvo com sucesso.'
  } catch (e) {
    erro.value = true
    mensagem.value = 'Erro ao salvar. Verifique os dados e suas permissões.'
  }
}

async function excluir() {
  if (!confirm('Tem certeza que deseja excluir esta solicitação?')) return
  await api.delete(`/solicitacoes/${route.params.id}/`)
  router.push('/')
}

async function comentar() {
  if (!novoComentario.value.trim()) return
  await api.post(`/solicitacoes/${route.params.id}/comentar/`, {
    texto: novoComentario.value,
  })
  novoComentario.value = ''
  carregar()
}

onMounted(carregar)
</script>

<style scoped>
.voltar { background: none; border: none; color: #1f2937; cursor: pointer; margin-bottom: 1rem; }
.form { display: flex; flex-direction: column; gap: 0.5rem; background: white; padding: 1.5rem; border-radius: 8px; }
input, textarea, select { padding: 0.5rem; }
.acoes { display: flex; gap: 0.5rem; margin-top: 1rem; }
button { padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer; background: #1f2937; color: white; }
.perigo { background: #b91c1c; }
.erro { color: #b91c1c; }
.sucesso { color: #15803d; }
.historico, .comentarios { background: white; padding: 1.5rem; border-radius: 8px; margin-top: 1rem; }
.form-comentario { display: flex; gap: 0.5rem; margin-top: 1rem; }
.form-comentario input { flex: 1; }
</style>
