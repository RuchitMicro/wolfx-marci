from django.urls import path
from .views import WhatsAppWebhookView, HealthView

urlpatterns = [
    path('webhook/whatsapp/',   WhatsAppWebhookView.as_view(),  name='whatsapp-webhook'),
    path('health/',             HealthView.as_view(),           name='health'),
]
