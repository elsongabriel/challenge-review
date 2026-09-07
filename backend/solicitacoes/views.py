from django.contrib.auth.models import User
from django_filters import rest_framework as django_filters
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Solicitacao, HistoricoStatus, Comentario
from .serializers import (
    SolicitacaoSerializer,
    SolicitacaoDetailSerializer,
    ComentarioSerializer,
)


class SolicitacaoFilter(django_filters.FilterSet):
    class Meta:
        model = Solicitacao
        fields = ['status', 'prioridade']


class SolicitacaoViewSet(viewsets.ModelViewSet):
    queryset = Solicitacao.objects.all().order_by('-criado_em')
    serializer_class = SolicitacaoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = SolicitacaoFilter
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['titulo']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SolicitacaoDetailSerializer
        return SolicitacaoSerializer

    def perform_create(self, serializer):
        serializer.save(autor=self.request.user)

    def perform_update(self, serializer):
        # Guarda o status anterior para registrar no histórico, caso mude.
        instance = self.get_object()
        status_anterior = instance.status
        solicitacao = serializer.save()
        if solicitacao.status != status_anterior:
            HistoricoStatus.objects.create(
                solicitacao=solicitacao,
                status_anterior=status_anterior,
                status_novo=solicitacao.status,
                alterado_por=self.request.user,
            )

    def perform_destroy(self, instance):
        instance.delete()

    @action(detail=True, methods=['post'])
    def comentar(self, request, pk=None):
        solicitacao = self.get_object()
        serializer = ComentarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(autor=request.user, solicitacao=solicitacao)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
