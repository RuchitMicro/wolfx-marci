from django.urls import path
from .views import (
    DashboardView,
    SystemHealthPartialView,
    AgentStatusPartialView,
    CostsPartialView,
    LiveLogPartialView,
    LogDetailView,
)

urlpatterns = [
    path('',                        DashboardView.as_view(),            name='dashboard'),
    path('partials/health/',        SystemHealthPartialView.as_view(),  name='dashboard-health'),
    path('partials/agents/',        AgentStatusPartialView.as_view(),   name='dashboard-agents'),
    path('partials/costs/',         CostsPartialView.as_view(),         name='dashboard-costs'),
    path('partials/live-log/',      LiveLogPartialView.as_view(),       name='dashboard-live-log'),
    path('logs/<int:pk>/',          LogDetailView.as_view(),            name='dashboard-log-detail'),
]
