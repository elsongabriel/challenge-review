from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SolicitacaoViewSet

router = DefaultRouter()
router.register('solicitacoes', SolicitacaoViewSet, basename='solicitacao')

urlpatterns = [
    path('', include(router.urls)),
]
