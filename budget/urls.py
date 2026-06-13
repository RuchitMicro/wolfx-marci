from django.urls import path
from .views import TokenUsageLogView

urlpatterns = [
    path('usage-logs/', TokenUsageLogView.as_view(), name='usage-log-list'),
]
