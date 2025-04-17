from django.apps import AppConfig


class McpServerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mcp_server'

    def ready(self):
        # Import tools here to ensure decorators are registered
        import mcp_server.tools
