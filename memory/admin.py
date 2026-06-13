from django.contrib import admin
from .models import ConversationLog, EpisodicMemory, EntityMemory, PersonEntity


@admin.register(ConversationLog)
class ConversationLogAdmin(admin.ModelAdmin):
    list_display    = ['channel_id', 'sender_name', 'role', 'intent', 'tokens_used', 'created_at']
    list_filter     = ['role', 'intent']
    ordering        = ['-created_at']


@admin.register(EpisodicMemory)
class EpisodicMemoryAdmin(admin.ModelAdmin):
    list_display    = ['channel_id', 'sender', 'scope', 'session_end']
    list_filter     = ['scope']
    ordering        = ['-session_end']


@admin.register(EntityMemory)
class EntityMemoryAdmin(admin.ModelAdmin):
    list_display    = ['entity_type', 'entity_name', 'scope', 'confidence', 'last_researched']
    list_filter     = ['entity_type', 'scope']
    ordering        = ['-updated_at']


@admin.register(PersonEntity)
class PersonEntityAdmin(admin.ModelAdmin):
    list_display    = ['phone_number', 'whatsapp_name', 'real_name', 'trust_level', 'last_active']
    list_filter     = ['trust_level']
    ordering        = ['-last_active']
