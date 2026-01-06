from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProviderViewSet, PaymentViewSet, DashboardView, generate_receipt

router = DefaultRouter()
router.register(r'providers', ProviderViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('receipt/<int:pk>/', generate_receipt, name='download-receipt'),
]
