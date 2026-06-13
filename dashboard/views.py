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
