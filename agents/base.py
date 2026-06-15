"""
agents/base.py

BaseAgent — the foundation of the wolfx-marci agent platform.

Every agent in this system extends this class.
The subagent implements handle() only.
Everything else — LangGraph wiring, tool loading, LLM client,
process pipeline — is handled here and inherited.

Current state: memory, budget, and identity are stubbed.
Each stub is clearly marked with TODO and the method that will replace it.
The process() interface is frozen — it will not change as stubs are implemented.
"""

import logging

from typing         import Any
from django.conf    import settings

from langgraph.graph            import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai           import ChatOpenAI
from langchain_core.messages    import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.tools       import BaseTool as LangChainBaseTool

from typing_extensions import TypedDict

logger = logging.getLogger(__name__)


# ── Agent State ──────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    """
    State object that flows through every LangGraph node.
    Clean, inspectable, serialisable.
    Passed by reference — nodes mutate and return it.
    """
    messages        :   list        # Full conversation including tool results
    sender          :   str         # Raw sender phone number
    sender_name     :   str         # Resolved display name (stub → phone number for now)
    intent          :   str         # Classified intent (stub → 'general' for now)
    context         :   str         # Pre-composed memory context (stub → '' for now)
    channel_id      :   str         # Which channel this came from
    iterations      :   int         # How many tool call cycles have happened
    final_reply     :   str         # Populated when agent is done


# ── BaseAgent ────────────────────────────────────────────────────────────────

class BaseAgent:
    """
    Base class for all wolfx-marci agents.

    Subagents declare:
        agent_type              — string identifier, maps to AGENT_REGISTRY
        memory_layers           — which memory layers to retrieve
        default_context_level   — none | minimal | standard | full
        known_intents           — list of intent strings this agent understands

    Subagents implement:
        handle()                — routing logic, calls run_graph() by default

    Everything else is inherited and handled here.
    """

    agent_type:             str     = None
    memory_layers:          list    = ['conversation']
    default_context_level:  str     = 'standard'
    known_intents:          list    = ['general']

    # ── Init ─────────────────────────────────────────────────────────────────

    def __init__(self, config):
        """
        config: AgentConfig Django model instance.
        Loads tools, builds LLM clients, builds LangGraph graph.
        Called once per agent instantiation.
        """
        self.config     = config
        self.tools      = self._load_tools()
        self.llm        = self._build_llm(model=getattr(settings, 'OPENAI_MODEL_DEFAULT', 'gpt-5-nano'))
        self.fast_llm   = self._build_llm(model=getattr(settings, 'OPENAI_MODEL_NANO', 'gpt-5-nano'))
        self.checkpointer = MemorySaver()   # TODO: swap to PostgresSaver in production
        self.graph      = self._build_graph()

        logger.info(f'[BaseAgent] Initialised: {self.config.name} ({self.agent_type})')

    # ── Public Interface ──────────────────────────────────────────────────────

    def process(self, message: str, sender: str, channel_binding) -> str:
        """
        Public entry point. Called by the channel dispatcher.
        Signature is frozen — do not change even as stubs are replaced.

        Pipeline:
            1. Identity resolution   (stub)
            2. Intent classification (stub)
            3. Memory retrieval      (stub)
            4. Budget check          (stub)
            5. handle()              → subagent
            6. Episode storage       (stub)
            7. Token recording       (stub)

        Returns the final reply string to be sent to the channel.
        """
        logger.info(f'[{self.config.name}] Processing message from {sender}: {message[:80]}')

        # ── Step 1: Identity resolution ──
        # TODO: replace with PersonEntity.resolve(sender, pushname)
        sender_name = self._stub_resolve_identity(sender)

        # ── Step 2: Intent classification ──
        # TODO: replace with IntentClassifier(self.fast_llm, self.known_intents).classify(message)
        intent = self._stub_classify_intent(message)

        # ── Step 3: Memory retrieval ──
        # TODO: replace with MemoryManager(self.config).retrieve(intent, sender, channel_binding)
        context = self._stub_get_context(intent)

        # ── Step 4: Budget check ──
        # TODO: replace with BudgetEnforcer(self.config).check_or_raise()
        self._stub_budget_check()

        # ── Step 5: Delegate to subagent ──
        try:
            reply = self.handle(
                message     = message,
                context     = context,
                sender_name = sender_name,
                intent      = intent,
                channel_id  = channel_binding.channel_id,
            )
        except Exception as exc:
            logger.exception(f'[{self.config.name}] handle() error: {exc}')
            reply = f'Something went wrong on my end. Please try again.'

        # ── Step 6: Episode storage ──
        # TODO: replace with MemoryManager.store_episode(message, reply, sender, channel_binding)
        self._stub_store_episode(message, reply, sender, channel_binding.channel_id)

        # ── Step 7: Token recording ──
        # TODO: replace with BudgetEnforcer.record_usage(tokens_used, model, intent)
        self._stub_record_usage()

        logger.info(f'[{self.config.name}] Reply generated: {reply[:80]}')
        return reply

    # ── Subagent Interface ────────────────────────────────────────────────────

    def handle(self, message: str, context: str, sender_name: str, intent: str, channel_id: str) -> str:
        """
        Override in subagents for custom routing logic.
        Default implementation runs run_graph() directly.
        """
        return self.run_graph(message, context, sender_name, intent, channel_id)

    # ── LangGraph Execution ───────────────────────────────────────────────────

    def run_graph(self, message: str, context: str, sender_name: str, intent: str, channel_id: str) -> str:
        """
        Executes the LangGraph ReAct loop.
        Builds initial state, runs the graph, extracts final reply.
        """
        thread_id = f'{self.agent_type}:{channel_id}:{sender_name}'

        initial_state: AgentState = {
            'messages':     [HumanMessage(content=message)],
            'sender':       sender_name,
            'sender_name':  sender_name,
            'intent':       intent,
            'context':      context,
            'channel_id':   channel_id,
            'iterations':   0,
            'final_reply':  '',
        }

        config = {
            'configurable': {
                'thread_id': thread_id,
            },
            'recursion_limit': self.config.max_iterations * 3,
        }

        try:
            final_state = self.graph.invoke(initial_state, config=config)
            return final_state.get('final_reply', 'I had trouble forming a response. Please try again.')
        except Exception as exc:
            logger.exception(f'[{self.config.name}] Graph execution error: {exc}')
            return 'Something went wrong during processing. Please try again.'

    # ── LangGraph Graph Builder ───────────────────────────────────────────────

    def _build_graph(self) -> StateGraph:
        """
        Builds the LangGraph StateGraph with three nodes:
            reason      → LLM decides what to do next
            tool_call   → execute a tool, feed result back
            end         → extract final reply and finish

        Conditional edges:
            reason → tool_call  if LLM wants to call a tool
            reason → end        if LLM is done
            tool_call → reason  always (feed result back for next reasoning step)
        """
        graph = StateGraph(AgentState)

        # ── Nodes ──
        graph.add_node('reason',    self._node_reason)
        graph.add_node('tool_call', self._node_tool_call)
        graph.add_node('end',       self._node_end)

        # ── Entry ──
        graph.set_entry_point('reason')

        # ── Edges ──
        graph.add_conditional_edges(
            'reason',
            self._route_after_reason,
            {
                'tool_call':    'tool_call',
                'end':          'end',
            }
        )
        graph.add_edge('tool_call', 'reason')
        graph.add_edge('end', END)

        return graph.compile(checkpointer=self.checkpointer)

    # ── LangGraph Nodes ───────────────────────────────────────────────────────

    def _node_reason(self, state: AgentState) -> AgentState:
        """
        Reasoning node. Calls LLM with current messages and available tools.
        LLM either calls a tool or produces a final response.
        """
        system_prompt = self._build_system_prompt(state['context'], state['sender_name'])

        messages_for_llm = [SystemMessage(content=system_prompt)] + state['messages']

        llm_with_tools = (
            self.llm.bind_tools(self._get_langchain_tools())
            if self.tools else self.llm
        )

        response = llm_with_tools.invoke(messages_for_llm)

        return {
            **state,
            'messages':     state['messages'] + [response],
            'iterations':   state['iterations'] + 1,
        }

    def _node_tool_call(self, state: AgentState) -> AgentState:
        """
        Tool execution node.
        Extracts tool call from last message, executes it, appends result.
        """
        last_message = state['messages'][-1]
        tool_results = []

        for tool_call in last_message.tool_calls:
            tool_name   = tool_call['name']
            tool_args   = tool_call['args']
            tool_id     = tool_call['id']

            logger.info(f'[{self.config.name}] Tool call: {tool_name} args={tool_args}')

            tool        = self._get_tool_by_name(tool_name)
            if tool:
                try:
                    result = tool.run(tool_args)
                except Exception as exc:
                    result = f'Tool error: {str(exc)}'
                    logger.warning(f'[{self.config.name}] Tool {tool_name} failed: {exc}')
            else:
                result = f'Tool {tool_name} not found.'
                logger.warning(f'[{self.config.name}] Unknown tool requested: {tool_name}')

            tool_results.append(
                ToolMessage(content=str(result), tool_call_id=tool_id)
            )

        return {
            **state,
            'messages': state['messages'] + tool_results,
        }

    def _node_end(self, state: AgentState) -> AgentState:
        """
        End node. Extracts the final text reply from the last AI message.
        """
        last_message = state['messages'][-1]
        final_reply  = getattr(last_message, 'content', '') or ''

        return {
            **state,
            'final_reply': final_reply,
        }

    # ── Routing ───────────────────────────────────────────────────────────────

    def _route_after_reason(self, state: AgentState) -> str:
        """
        Conditional edge router after reasoning node.
        Routes to tool_call if LLM wants a tool, end otherwise.
        Also routes to end if max iterations exceeded.
        """
        if state['iterations'] >= self.config.max_iterations:
            logger.warning(f'[{self.config.name}] Max iterations reached — forcing end.')
            return 'end'

        last_message = state['messages'][-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return 'tool_call'

        return 'end'

    # ── Prompt Builder ────────────────────────────────────────────────────────

    def _build_system_prompt(self, context: str, sender_name: str) -> str:
        """
        Assembles the full system prompt:
            GlobalPrompt + AgentConfig.system_prompt + AgentConfig.personality_prompt + context
        """
        parts = []

        # Layer 1 — Global non-negotiables
        global_prompt = self._get_global_prompt()
        if global_prompt:
            parts.append(global_prompt)

        # Layer 2 — Agent system prompt
        if self.config.system_prompt and self.config.system_prompt.strip():
            parts.append(self.config.system_prompt.strip())

        # Layer 3 — Personality
        if self.config.personality_prompt and self.config.personality_prompt.strip():
            parts.append(self.config.personality_prompt.strip())

        # Layer 4 — Runtime context (memory pre-composition output)
        if context and context.strip():
            parts.append(f'==CONTEXT==\n{context.strip()}')

        # Layer 5 — Sender identity
        parts.append(f'You are talking to: {sender_name}')

        return '\n\n'.join(parts)

    # ── LLM Builder ──────────────────────────────────────────────────────────

    def _build_llm(self, model: str) -> ChatOpenAI:
        """Builds a ChatOpenAI client for the given model."""
        return ChatOpenAI(
            model       = model,
            api_key     = settings.OPENAI_API_KEY,
            max_tokens  = self.config.max_tokens_per_call,
            temperature = 0.3,
        )

    # ── Tool Helpers ──────────────────────────────────────────────────────────

    def _load_tools(self) -> list:
        """
        Loads tool instances from TOOL_REGISTRY based on config.enabled_tools.
        Returns empty list if no tools configured — agent runs in pure LLM mode.
        """
        from tools.registry import get_tools_for_agent
        return get_tools_for_agent(self.config.enabled_tools or [])

    def _get_langchain_tools(self) -> list[LangChainBaseTool]:
        """Returns tools as LangChain tool objects for LLM binding."""
        return [t.to_langchain_tool() for t in self.tools if hasattr(t, 'to_langchain_tool')]

    def _get_tool_by_name(self, name: str):
        """Returns a tool instance by name, or None if not found."""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None

    # ── Global Prompt ─────────────────────────────────────────────────────────

    def _get_global_prompt(self) -> str:
        """Returns the active GlobalPrompt content, or empty string if none set."""
        try:
            from config.models import GlobalPrompt
            gp = GlobalPrompt.objects.filter(is_active=True).first()
            return gp.content.strip() if gp else ''
        except Exception as exc:
            logger.warning(f'[BaseAgent] Could not load GlobalPrompt: {exc}')
            return ''

    # ── Stubs — replace these as each layer is implemented ───────────────────

    def _stub_resolve_identity(self, sender: str) -> str:
        """
        STUB — Layer: memory/models/person_entity.py
        TODO: replace with PersonEntity.resolve(sender, pushname).display_name
        """
        return sender.split('@')[0]

    def _stub_classify_intent(self, message: str) -> str:
        """
        STUB — Layer: agents/classifier.py
        TODO: replace with IntentClassifier(self.fast_llm, self.known_intents).classify(message)
        Returns 'general' for all messages until classifier is implemented.
        """
        return 'general'

    def _stub_get_context(self, intent: str) -> str:
        """
        STUB — Layer: memory/manager.py + memory/precompose.py
        TODO: replace with MemoryManager.retrieve(intent) → PreComposer.compose()
        Returns empty context until memory layer is implemented.
        """
        return ''

    def _stub_budget_check(self):
        """
        STUB — Layer: budget/enforcer.py
        TODO: replace with BudgetEnforcer(self.config, redis_client).check_or_raise()
        Does nothing until budget layer is implemented.
        """
        pass

    def _stub_store_episode(self, message: str, reply: str, sender: str, channel_id: str):
        """
        STUB — Layer: memory/manager.py
        TODO: replace with MemoryManager.store_episode(message, reply, person, channel_binding)
        Logs only until memory layer is implemented.
        """
        logger.debug(f'[BaseAgent] Episode stub — message: {message[:40]} reply: {reply[:40]}')

    def _stub_record_usage(self):
        """
        STUB — Layer: budget/tracker.py
        TODO: replace with BudgetEnforcer.record_usage(tokens_used, model, intent)
        Does nothing until budget layer is implemented.
        """
        pass