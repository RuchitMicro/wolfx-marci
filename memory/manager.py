from memory.models import ConversationLog, EpisodicMemory, EntityMemory, PersonEntity


class MemoryManager:
    """
    Coordinates all four memory layers.
    Called by BaseAgent.process() before every agent invocation.
    """

    def __init__(self, agent_config):
        self.config = agent_config

    def resolve_identity(self, phone_number: str, pushname: str = '') -> PersonEntity:
        raise NotImplementedError('Resolve sender identity via PersonEntity.resolve().')

    def retrieve_minimal(self, person: PersonEntity, channel_binding) -> dict:
        raise NotImplementedError('Return identity + last 2 conversation messages only.')

    def retrieve_standard(self, person: PersonEntity, channel_binding, message: str) -> dict:
        raise NotImplementedError('Return identity + episodic summary + last N conversation messages.')

    def retrieve_full(self, person: PersonEntity, channel_binding, message: str) -> dict:
        raise NotImplementedError('Return all layers — identity, episodic, semantic pgvector search, entity memory.')

    def store_episode(self, message: str, reply: str, person: PersonEntity, channel_binding):
        raise NotImplementedError('Save ConversationLog entries for user message and assistant reply.')

    def summarise_session(self, channel_id: str, sender: str):
        raise NotImplementedError('Background task — summarise recent ConversationLog entries into EpisodicMemory.')

    def get_entity(self, entity_name: str, scope: str = 'global', scope_id: str = ''):
        raise NotImplementedError('Retrieve EntityMemory by name and scope.')

    def store_entity(self, entity_name: str, data: dict, scope: str = 'global', scope_id: str = ''):
        raise NotImplementedError('Create or update EntityMemory for this entity.')

    def is_stale(self, entity: EntityMemory) -> bool:
        raise NotImplementedError('Return True if entity research is older than config.memory_staleness_days.')
