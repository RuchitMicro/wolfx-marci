# wolfx-marci

The intelligence layer for WOLFx. A standalone Django agent platform that receives messages from any channel, thinks, uses tools, remembers, and responds. The WhatsApp bot is one channel. The CRM is one data source. The architecture supports any channel and any tool without changing the core.

---

## What This Is Not

This is not a chatbot wrapper. It is not a prompt-engineering project. It is a multi-agent platform with layered memory, a tool registry, an inter-agent bus, budget controls, and a real-time observability dashboard.

---

## Architecture

Six independent layers. Nothing in any layer knows about the others except through defined interfaces.

### 1. Channels
Entry point. Receives messages from the outside world and hands them to the right agent. Does nothing else — no logic, no memory, no LLM calls. Current: WhatsApp via wweb-mcp. Planned: Slack.

### 2. Config
Control plane. Everything configurable lives in Django admin — no code changes needed for operations. Three core models:
- `GlobalPrompt` — versioned non-negotiable instructions applied to all agents
- `AgentConfig` — per-agent settings: prompts, tools, memory layers, budget limits
- `ChannelBinding` — maps a WhatsApp group or Slack channel to a specific agent

### 3. Memory
Four layers coordinated by `MemoryManager`:
- **Layer 1 — Conversation** — short-term in-session message history
- **Layer 2 — Episodic** — summarised past sessions, created by background Celery task
- **Layer 3 — Semantic** — pgvector embeddings of everything ever learned, retrieved by similarity
- **Layer 4 — Entity** — structured facts about companies and people, public (global) and private (group-scoped)

Identity resolution is automatic. Marci learns who everyone is from their first message via WhatsApp pushname — no manual mapping needed.

### 4. Agents
Intelligence layer. `BaseAgent` handles all infrastructure: identity resolution, intent classification, memory retrieval, pre-composition, budget enforcement, tool loading, LangGraph ReAct execution, episode storage. A subagent is a single Python file that extends `BaseAgent` and declares its intents, tools, and memory layers. It implements one method. Everything else is inherited.

Current agents:
| Agent | Role |
|-------|------|
| `MarciSalesAgent` | CRM queries, strategic advice, outreach drafts, reminders |
| `MarciTeamAgent` | WOLFx knowledge, team coordination, reminders. Never accesses CRM |
| `ResearchAgent` | Company and person research via web and LinkedIn tools |
| `BroadcastAgent` | Scheduled content generation and posting to community groups |

### 5. Tools
What agents can do. Each tool is a self-contained Python class with a name, description, input schema, output schema, and fallback chain. Agents only see tools in their `enabled_tools` list.

Current tools:
| Tool | Description |
|------|-------------|
| `crm_query` | Calls wolfx-networking MCP read-only API |
| `web_search` | Tavily with DuckDuckGo fallback |
| `web_browse` | Playwright full page extraction via web-mcp |
| `draft_writer` | LLM-based outreach message generation |
| `company_research` | web_search + web_browse + LLM summarise + EntityMemory storage |
| `linkedin_lookup` | Playwright LinkedIn scraper with fallback |
| `reminder` | Creates ScheduledTask records for time-based alerts |

### 6. Bus
Inter-agent communication. When one agent needs another to do something — research a company, draft a sequence — it creates a task on the `AgentBus` and replies immediately. Celery picks up the task, executes it, and fires a callback to the original channel. Agents never block waiting for each other.

---

## Request Lifecycle

```
Message arrives in WhatsApp group
      ↓
Channel dispatcher looks up ChannelBinding
      ↓
BaseAgent: identity resolution (PersonEntity lookup)
      ↓
BaseAgent: intent classification (one nano LLM call)
      ↓
BaseAgent: scoped memory retrieval (none / minimal / standard / full)
      ↓
BaseAgent: pre-composition (cheap nano call synthesises memory into context)
      ↓
BaseAgent: budget check (Redis token counters)
      ↓
Subagent: handle() → LangGraph ReAct loop → tool calls → reply
      ↓
BaseAgent: store episode, record token usage
      ↓
Channel: send reply via wweb-mcp
```

---

## Memory Scoping

| Scope | What It Contains | Who Can Access |
|-------|-----------------|----------------|
| Global | Public company facts, industry knowledge, research | All agents, all groups |
| Group | Pipeline context, rejected prospects, pricing discussed | Only the group where it was created |
| User | Personal reminders, preferences, interaction history | Only when that person is talking |

---

## Intent Classification

Before any memory retrieval, a cheap nano LLM call classifies the message into an intent and assigns a context requirement level:

| Context Level | What Gets Retrieved | When Used |
|---------------|---------------------|-----------|
| `none` | Nothing — just identity | Reminders, simple confirmations |
| `minimal` | Identity + last 2 messages | Greetings, simple factual questions |
| `standard` | Identity + episodic + last N messages | Most conversational queries |
| `full` | All layers including pgvector search | Research, complex analysis, CRM queries |

---

## Proactive Loop

Celery Beat fires `ScheduledTask` records. Three trigger types:

| Trigger | Description | Example |
|---------|-------------|---------|
| `time` | One-time at a specific datetime | "Remind me at 5pm about WASSL call" |
| `schedule` | Recurring cron expression | "Post SEO tip every Monday 9am" |
| `signal` | External event detected | "Alert Heni when prospect announces funding" |

Scheduled tasks can optionally fetch fresh context at fire time — a reminder about Harshi's performance pulls her latest CRM stats at the moment it fires, not when it was created.

---

## Cost Controls

Three operating modes via `AGENT_MODE` environment variable:

| Mode | Behaviour | When Used |
|------|-----------|-----------|
| `mock` | Zero API calls, all tools return static fixtures | Development |
| `cheap` | gpt-5-nano for everything, real API calls | Integration testing |
| `full` | Configured models per tool, real calls | Production |

Multi-model routing — cheap nano calls for intent classification and simple responses, stronger models only for complex reasoning tasks. Redis token tracking per agent per day with graduated alerts at 80% of daily budget. OpenAI hard spend cap as final backstop.

---

## Dashboard

Single page at `/dashboard/`. Four zones auto-refreshing every 5 seconds via HTMX:

| Zone | Contents |
|------|----------|
| System Health | Redis, PostgreSQL, Celery, wweb-mcp, frp tunnel, Zeus RAM — green/red dots |
| Agent Status | One row per agent, lock status, last reply time, per-agent kill switch |
| Costs Today | Token usage per agent with progress bars and estimated USD spend |
| Live Log Feed | Every message processed — sender, intent, outcome, latency. Click for full detail |

Kill switches at three levels: clear agent lock, pause single agent, global pause all agents.

---

## Project Structure

```
wolfx-marci/
│
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
│
├── wolfx_marci/                    # Django project root
│   ├── settings.py
│   ├── celery.py
│   ├── urls.py
│   └── wsgi.py
│
├── config/                         # Django app — agent configuration
│   ├── admin.py
│   ├── urls.py
│   ├── views/
│   └── models/
│       ├── global_prompt.py        # Versioned non-negotiables for all agents
│       ├── agent_config.py         # Per-agent settings
│       ├── channel_binding.py      # Group → agent mapping
│       ├── agent_task.py           # Inter-agent bus tasks
│       └── scheduled_task.py       # Reminders + broadcasts
│
├── memory/                         # Django app — all memory layers
│   ├── manager.py                  # MemoryManager — coordinates all layers
│   ├── precompose.py               # Pre-composition LLM call
│   ├── views/
│   └── models/
│       ├── conversation_log.py     # Layer 1 — in-session history
│       ├── episodic_memory.py      # Layer 2 — summarised past sessions
│       ├── entity_memory.py        # Layer 3+4 — pgvector + structured facts
│       └── person_entity.py        # Identity resolution
│
├── agents/                         # Pure Python — no Django models
│   ├── base.py                     # BaseAgent — all infrastructure
│   ├── registry.py                 # AGENT_REGISTRY + load_agent()
│   ├── classifier.py               # Intent classifier
│   └── implementations/
│       ├── marci_sales.py
│       ├── marci_team.py
│       ├── research_agent.py
│       └── broadcast_agent.py
│
├── tools/                          # Pure Python — no Django models
│   ├── base_tool.py                # BaseTool — error handling + fallbacks
│   ├── registry.py                 # TOOL_REGISTRY + get_tools_for_agent()
│   └── implementations/
│       ├── crm_query.py
│       ├── web_search.py
│       ├── web_browse.py
│       ├── draft_writer.py
│       ├── company_research.py
│       ├── linkedin_lookup.py
│       └── reminder.py
│
├── bus/                            # Django app — inter-agent communication
│   ├── agent_bus.py                # AgentBus — task creation + dispatch
│   └── tasks.py                    # Celery tasks
│
├── channels/                       # Pure Python — no Django models
│   ├── base_channel.py             # BaseChannel interface
│   └── implementations/
│       ├── whatsapp.py             # Thin dispatcher — receive + send only
│       └── slack.py                # Future
│
├── budget/                         # Django app — token tracking + enforcement
│   ├── enforcer.py                 # BudgetEnforcer — Redis counters
│   ├── tracker.py                  # Read-only usage views for dashboard
│   └── models/
│       └── usage_log.py            # TokenUsageLog — daily records
│
├── dashboard/                      # Django app — observability
│   ├── views.py                    # Four-zone single page + HTMX partials
│   └── templates/dashboard/
│       ├── index.html
│       └── partials/
│           ├── system_health.html
│           ├── agent_status.html
│           ├── costs.html
│           └── live_log.html
│
├── api/                            # Django app — webhook endpoints
│   └── views/
│       ├── whatsapp_webhook.py
│       └── health.py
│
└── packages/                       # Node.js MCP servers
    ├── wweb-mcp/                   # WhatsApp Web MCP (existing)
    └── web-mcp/                    # Puppeteer browsing MCP (new)
```

---

## Extension Model

| What to Add | How |
|-------------|-----|
| New agent | One `.py` in `agents/implementations/` + one line in `AGENT_REGISTRY` + one `AgentConfig` in admin |
| New tool | One `.py` in `tools/implementations/` + one line in `TOOL_REGISTRY` |
| New channel | Implement `BaseChannel` + register in channel dispatcher |
| New memory type | Extend `MemoryManager` + add Django model |

---

## Memory Trajectory

| Timeframe | What Marci Knows |
|-----------|-----------------|
| Day 1 | What her prompts tell her |
| Week 1 | Every team member by name via pushname auto-resolution |
| Month 1 | EntityMemory for every company the team has ever touched |
| Month 3 | Patterns the team hasn't noticed — surfacing insights proactively |
| Month 6 | Proactively flagging opportunities, overdue follow-ups, industry signals without being asked |

Intelligence compounds with usage. Every interaction teaches her something the next interaction benefits from.

---

## Related Projects

**wolfx-networking** — WOLFx CRM backend (Django + PostgreSQL on DigitalOcean). Exposes a read-only MCP API consumed by the `crm_query` tool. No AI code lives there. If it goes down, Marci degrades gracefully.

**wweb-mcp** — WhatsApp Web MCP server (Node.js + Puppeteer). Lives in `packages/wweb-mcp/`. Fires webhooks to wolfx-marci and sends replies via REST API.

**web-mcp** — Puppeteer browsing MCP server (Node.js). Lives in `packages/web-mcp/`. Used by the `web_browse` tool for full page extraction.

---

## Deployment

Deployed on Zeus (Dell OptiPlex 7040, 8GB RAM, Ubuntu 24.04 Server) via frp reverse tunnel to DigitalOcean public server.

```
Internet → DigitalOcean (public IP) → frp tunnel → Zeus (local)
                                             ↓
                                      wolfx-marci Django
                                      PostgreSQL + pgvector
                                      Redis
                                      Celery + Celery Beat
                                      wweb-mcp (Node.js)
                                      web-mcp (Node.js)
```

---

## Stack

| Component | Technology |
|-----------|-----------|
| Framework | Python 3.12 + Django 4.2 |
| Agent orchestration | LangGraph + LangChain |
| Semantic memory | PostgreSQL + pgvector |
| Task queue | Celery + Celery Beat |
| Cache + locks | Redis |
| Dashboard reactivity | HTMX |
| WhatsApp channel | wweb-mcp (Node.js + whatsapp-web.js) |
| Web browsing tool | web-mcp (Node.js + Playwright) |
| Embeddings | OpenAI text-embedding-3-small |
| LLM routing | gpt-5-nano (classification) + configurable per tool |
| Tunnel | frp v0.68.0 |# wolfx-marci
