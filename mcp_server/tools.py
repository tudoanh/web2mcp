# This file contains the implementation logic for the MCP tools using django-mcp.

# Import the mcp_app instance from django_mcp
from django_mcp import mcp_app as mcp
from asgiref.sync import sync_to_async

from crawler.models import CrawledPage
from django.db.models import Q
from datetime import datetime

# Note: Consider making these async if interactions become complex or involve I/O.
# django-mcp supports async functions.

@mcp.tool()
async def find_pages(keyword: str, domain: str = None, start_date: str = None, end_date: str = None) -> list[dict]:
    """
    Search crawled pages by keyword in title or summary.
    Optionally filters by domain and date range.
    """
    print(f"Executing find_pages: keyword='{keyword}', domain='{domain}', start='{start_date}', end='{end_date}'") # Basic logging

    filters = Q(title__icontains=keyword) | Q(summary__icontains=keyword)

    if domain:
        filters &= Q(domain=domain)

    try:
        if start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            filters &= Q(updated_at__date__gte=start_dt)
        if end_date:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
            filters &= Q(updated_at__date__lte=end_dt)
    except ValueError:
        # Handle invalid date format - perhaps raise an error or log it
        print(f"Invalid date format provided. Ignoring date filters.")
        # Or return an error structure? For now, just proceed without date filter.
        pass

    # Query the database asynchronously
    # Use sync_to_async to wrap the synchronous ORM call
    # list() ensures the QuerySet is evaluated within the sync context
    matching_pages_qs = CrawledPage.objects.filter(filters).order_by('-updated_at')[:50]
    matching_pages = await sync_to_async(list)(matching_pages_qs)

    # Format the results
    results_list = [
        {
            "url": page.url,
            "title": page.title,
            "summary": page.summary,
            "domain": page.domain,
            "updated_at": page.updated_at.isoformat() # Use ISO format for consistency
        }
        for page in matching_pages
    ]

    print(f"Found {len(results_list)} pages.") # Basic logging
    return results_list

@mcp.tool()
async def get_page_content(url: str) -> dict:
    """
    Get the stored HTML content for a specific crawled URL.
    """
    print(f"Executing get_page_content for URL: {url}") # Basic logging
    try:
        # Use sync_to_async for the synchronous ORM call
        page = await sync_to_async(CrawledPage.objects.get)(url=url)
        print(f"Found page content.") # Basic logging
        return {
            "url": page.url,
            "html_content": page.html_content
        }
    except CrawledPage.DoesNotExist:
        # This exception is raised by sync_to_async if the underlying sync function raises it
        print(f"Page not found.") # Basic logging
        # How should errors be represented in MCP tool results?
        # Returning a specific structure or raising an exception handled by the view?
        # For now, return an error dictionary.
        return {"error": "Page not found in database", "url": url}
    except Exception as e:
        print(f"Error retrieving page content: {e}") # Basic logging
        return {"error": f"An error occurred: {str(e)}", "url": url}
