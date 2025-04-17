"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

This file has been modified to mount the MCP server alongside the default Django application.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django # Import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Explicitly call django.setup() BEFORE importing models or anything
# that depends on Django settings. This needs to happen before importing
# mcp_server below, as that import chain leads to model loading.
django.setup()

# Explicitly call django.setup() BEFORE importing models or anything
# that depends on Django settings.
django.setup()

# Import django_mcp AFTER django.setup()
from django_mcp import mount_mcp_server

# Get the default Django ASGI application
django_http_app = get_asgi_application()

# Mount the MCP server using django-mcp
application = mount_mcp_server(django_http_app=django_http_app, mcp_base_path='/mcp')
