from django.urls import path
from .views import WhatsAppWebhookView, HealthView
from .views.health import WhatsAppQRView

urlpatterns = [
    path('webhook/whatsapp/',   WhatsAppWebhookView.as_view(),  name='whatsapp-webhook'),
    path('qr/',                 WhatsAppQRView.as_view(), name='whatsapp-qr'),
    path('health/',             HealthView.as_view(),           name='health'),
]
