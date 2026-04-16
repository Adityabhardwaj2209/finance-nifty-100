from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, ScoresViewSet, SectorViewSet

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'scores', ScoresViewSet)
router.register(r'sectors', SectorViewSet, basename='sectors')

urlpatterns = [
    path('', include(router.urls)),
]
