from django.db import models


class GlobalPrompt(models.Model):
    """
    Versioned global prompt applied to all agents as the base non-negotiable layer.
    Only one instance should be active at a time.
    """
    version     = models.CharField(max_length=20, unique=True)
    content     = models.TextField(help_text='Non-negotiable instructions applied to all agents.')
    is_active   = models.BooleanField(default=False, help_text='Only one GlobalPrompt should be active at a time.')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Global Prompt'
        verbose_name_plural = 'Global Prompts'
        ordering            = ['-created_at']

    def __str__(self):
        return f'v{self.version} ({"active" if self.is_active else "inactive"})'

    def save(self, *args, **kwargs):
        raise NotImplementedError('Override save() to enforce single active instance.')

    @classmethod
    def get_active(cls):
        raise NotImplementedError('Return the currently active GlobalPrompt instance.')
