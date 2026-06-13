#!/bin/bash
set -euo pipefail

APP="dashboard"

rm -f $APP/models.py $APP/views.py

mkdir -p $APP/templates/dashboard/partials

# ── views.py ──
cat > $APP/views.py << 'EOF'
from django.views import View
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator


@method_decorator(staff_member_required, name='dispatch')
class DashboardView(View):
    """
    Single page health dashboard.
    Four zones: system health, agent status, costs, live log feed.
    HTMX partials auto-refresh every 5 seconds.
    """

    def get(self, request):
        raise NotImplementedError('Render dashboard/index.html with initial context.')


@method_decorator(staff_member_required, name='dispatch')
class SystemHealthPartialView(View):
    """HTMX partial — Zone 1. Pings Redis, PostgreSQL, Celery, wweb-mcp, frp."""

    def get(self, request):
        raise NotImplementedError('Return dashboard/partials/system_health.html with live health status.')


@method_decorator(staff_member_required, name='dispatch')
class AgentStatusPartialView(View):
    """HTMX partial — Zone 2. One row per agent with lock status and kill switch."""

    def get(self, request):
        raise NotImplementedError('Return dashboard/partials/agent_status.html with agent states from Redis.')

    def post(self, request):
        raise NotImplementedError('Handle kill switch actions: clear_lock, pause_agent, global_pause.')


@method_decorator(staff_member_required, name='dispatch')
class CostsPartialView(View):
    """HTMX partial — Zone 3. Token usage and cost per agent today."""

    def get(self, request):
        raise NotImplementedError('Return dashboard/partials/costs.html with UsageTracker.get_all_agents_today().')


@method_decorator(staff_member_required, name='dispatch')
class LiveLogPartialView(View):
    """HTMX partial — Zone 4. Last 20 ConversationLog entries across all agents."""

    def get(self, request):
        raise NotImplementedError('Return dashboard/partials/live_log.html with last 20 ConversationLog entries.')


@method_decorator(staff_member_required, name='dispatch')
class LogDetailView(View):
    """Expandable detail view for a single ConversationLog entry."""

    def get(self, request, pk):
        raise NotImplementedError('Return full detail for one ConversationLog: prompt, SQL, tools called, tokens.')
EOF

# ── urls.py ──
cat > $APP/urls.py << 'EOF'
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
EOF

# ── templates ──
cat > $APP/templates/dashboard/index.html << 'EOF'
{% comment %}
Single page dashboard — four zones.
HTMX polls partials every 5 seconds.
TODO: implement full template with Poppins font, dark theme, 4-zone grid layout.
{% endcomment %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>wolfx-marci — Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <style>
        /* TODO: implement 4-zone grid layout */
        body { font-family: 'Poppins', sans-serif; background: #0a0a0a; color: #fff; margin: 0; padding: 0; }
    </style>
</head>
<body>
    <div id="zone-health"   hx-get="{% url 'dashboard-health' %}"   hx-trigger="every 5s" hx-swap="innerHTML">
        {% include 'dashboard/partials/system_health.html' %}
    </div>
    <div id="zone-agents"   hx-get="{% url 'dashboard-agents' %}"   hx-trigger="every 5s" hx-swap="innerHTML">
        {% include 'dashboard/partials/agent_status.html' %}
    </div>
    <div id="zone-costs"    hx-get="{% url 'dashboard-costs' %}"    hx-trigger="every 5s" hx-swap="innerHTML">
        {% include 'dashboard/partials/costs.html' %}
    </div>
    <div id="zone-log"      hx-get="{% url 'dashboard-live-log' %}" hx-trigger="every 5s" hx-swap="innerHTML">
        {% include 'dashboard/partials/live_log.html' %}
    </div>
</body>
</html>
EOF

cat > $APP/templates/dashboard/partials/system_health.html << 'EOF'
{% comment %}TODO: render Redis, PostgreSQL, Celery, wweb-mcp, frp status as green/red dots.{% endcomment %}
<p>system_health partial — TODO</p>
EOF

cat > $APP/templates/dashboard/partials/agent_status.html << 'EOF'
{% comment %}TODO: render one row per agent with lock status, last reply, kill switch button.{% endcomment %}
<p>agent_status partial — TODO</p>
EOF

cat > $APP/templates/dashboard/partials/costs.html << 'EOF'
{% comment %}TODO: render token usage per agent with progress bars and estimated cost.{% endcomment %}
<p>costs partial — TODO</p>
EOF

cat > $APP/templates/dashboard/partials/live_log.html << 'EOF'
{% comment %}TODO: render last 20 ConversationLog entries — sender, intent, outcome, latency. Clickable rows.{% endcomment %}
<p>live_log partial — TODO</p>
EOF

# ── admin.py ──
cat > $APP/admin.py << 'EOF'
from django.contrib import admin

# Dashboard has no models. Admin registered in config and memory apps.
EOF

# ── apps.py ──
cat > $APP/apps.py << 'EOF'
from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field  = 'django.db.models.BigAutoField'
    name                = 'dashboard'
    verbose_name        = 'Dashboard'
EOF

echo ""
echo "dashboard app structure created successfully."