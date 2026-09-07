from django.contrib.auth.models import User
from django.db import connections
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Solicitacao, Comentario


class SolicitacaoTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='ana', password='senha123')
        self.user2 = User.objects.create_user(username='bruno', password='senha123')
        self.solicitacao = Solicitacao.objects.create(
            titulo='Solicitação da Ana',
            descricao='teste',
            autor=self.user1,
        )

    def autenticar(self, user):
        self.client.force_authenticate(user=user)

    def test_usuario_autenticado_consegue_listar(self):
        self.autenticar(self.user1)
        response = self.client.get('/api/solicitacoes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_usuario_nao_autenticado_nao_acessa(self):
        response = self.client.get('/api/solicitacoes/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # -----------------------------------------------------------------
    # TODO (candidato): os testes abaixo descrevem regras de negócio do
    # desafio que ainda NÃO estão implementadas corretamente no código.
    # Implemente a correção no backend e então remova o skip para
    # confirmar que o teste passa.
    # -----------------------------------------------------------------

    def test_usuario_nao_pode_editar_solicitacao_de_outro(self):
        """Regra: um usuário só pode editar suas próprias solicitações."""
        self.autenticar(self.user2)
        response = self.client.patch(
            f'/api/solicitacoes/{self.solicitacao.id}/',
            {'titulo': 'Tentando editar solicitação alheia'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_deve_ser_soft_delete(self):
        """Regra: exclusão deve ser soft delete, não remover do banco."""
        self.autenticar(self.user1)
        self.client.delete(f'/api/solicitacoes/{self.solicitacao.id}/')
        self.assertTrue(
            Solicitacao.objects.filter(id=self.solicitacao.id).exists(),
            'A solicitação foi removida do banco — esperado soft delete.',
        )

    def test_solicitacao_excluida_nao_aparece_na_listagem(self):
        """Após o soft delete, a solicitação não deve mais aparecer na listagem."""
        self.autenticar(self.user1)
        self.client.delete(f'/api/solicitacoes/{self.solicitacao.id}/')
        response = self.client.get('/api/solicitacoes/')
        ids = [s['id'] for s in response.data]
        self.assertNotIn(self.solicitacao.id, ids)

    def test_nao_permite_reabrir_solicitacao_concluida_diretamente(self):
        """Regra: não deve ser possível ir de 'concluida' para 'aberta' direto."""
        self.solicitacao.status = 'concluida'
        self.solicitacao.save()
        self.autenticar(self.user1)
        response = self.client.patch(
            f'/api/solicitacoes/{self.solicitacao.id}/',
            {'status': 'aberta'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_permite_transicao_de_status_valida(self):
        """Uma transição permitida (ex.: concluida -> em_andamento) deve funcionar."""
        self.solicitacao.status = 'concluida'
        self.solicitacao.save()
        self.autenticar(self.user1)
        response = self.client.patch(
            f'/api/solicitacoes/{self.solicitacao.id}/',
            {'status': 'em_andamento'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_nao_permite_titulo_em_branco(self):
        """Regra: título não pode ser salvo vazio ou só com espaços."""
        self.autenticar(self.user1)
        response = self.client.post(
            '/api/solicitacoes/',
            {'titulo': '   ', 'descricao': 'teste'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _queries_no_detalhe(self, num_comentarios):
        solic = Solicitacao.objects.create(titulo='Com comentarios', autor=self.user1)
        for i in range(num_comentarios):
            Comentario.objects.create(solicitacao=solic, autor=self.user2, texto=f'c{i}')
        self.autenticar(self.user1)
        with CaptureQueriesContext(connections['default']) as ctx:
            self.client.get(f'/api/solicitacoes/{solic.id}/')
        return len(ctx.captured_queries)

    def test_detalhe_nao_faz_query_por_comentario(self):
        """O nº de queries do detalhe não deve crescer com a quantidade de comentários (N+1)."""
        poucos = self._queries_no_detalhe(2)
        muitos = self._queries_no_detalhe(10)
        self.assertEqual(
            poucos, muitos,
            f'Query count cresceu com o nº de comentários ({poucos} -> {muitos}): possível N+1.',
        )
