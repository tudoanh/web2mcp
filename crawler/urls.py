from django.urls import path
from . import views

app_name = 'crawler' # Define an application namespace

urlpatterns = [
    path('', views.submit_url_view, name='submit_url'),
    # API endpoints for MCP server
    path('api/search_pages/', views.search_pages_api, name='api_search_pages'),
    path('api/get_content/', views.get_content_api, name='api_get_content'),
    # API endpoint for checking crawl status
    path('api/crawl_status/<int:page_id>/', views.crawl_status_api, name='api_crawl_status'),
    # Add other app-specific URLs here later
]
