# Progress

*This file tracks what works, what's left to build, the current status, known issues, and the evolution of project decisions.*

## Current Status (as of 2025-04-17 10:31 AM)

*   **Phase:** Initial Implementation (UI, Structure, MCP Server) & Crawler Development.
*   **Overall Progress:** Project planned, Memory Bank initialized and updated. Core Django structure for the `crawler` app is set up (model, migrations, basic form, view, template, URL routing). **MCP server functionality successfully migrated to use `django-mcp`**. Dependencies updated. The application can run via ASGI (`uvicorn core.asgi:application`), display the form, accept URL submissions (but doesn't crawl yet), and serve MCP requests at `/mcp`.

## What Works

*   Django project runs (`python manage.py runserver`).
*   The `crawler` app is registered.
*   Database migrations for `CrawledPage` model are applied.
*   The URL submission form is displayed at the root URL (`/`).
*   The form validates input URL format (HTTP/HTTPS).
*   Submitting a valid URL shows a success message (placeholder action).
*   Submitting an invalid URL shows form errors.
*   **Project Documentation:**
    *   `README.md` created with project overview, setup, usage, and screenshot.
*   **Django API (`/api/search_pages/`):**
    *   Accepts `keyword` parameter.
    *   Accepts optional `domain`, `start_date`, `end_date` parameters for filtering.
    *   Returns JSON results including `url`, `title`, `summary`, `domain`, `updated_at`.
*   **Django API (`/api/get_content/`):**
    *   Accepts `url` parameter.
    *   Returns JSON with `url` and `html_content`. (Note: These APIs are no longer directly exposed but their logic is used by the `get_page_content` MCP tool).
*   **MCP Server (`django-mcp`):**
    *   Server runs via ASGI mount in `core/asgi.py`.
    *   Tools (`find_pages`, `get_page_content`) defined in `mcp_server/tools.py` are discoverable and executable via MCP requests to `/mcp`.

## What's Left to Build (High-Level)

1.  **Crawling Engine (`crawler/tasks.py`):**
    *   Implement URL fetching (`requests`) with basic error handling.
    *   Implement HTML parsing (`BeautifulSoup4`).
    *   Implement data extraction (title, meta description, full HTML content).
    *   Implement link extraction and filtering (same-domain, avoid non-HTML).
    *   Manage visited URLs to prevent loops/redundancy.
2.  **Crawler Integration (`crawler/views.py`):**
    *   Connect the `submit_url_view` POST handler to trigger the crawl process defined in `crawler/tasks.py`.
    *   Ensure `CrawledPage` records are created/updated correctly by the crawler logic.
3.  **Process Management:** Implement initial crawl execution (e.g., synchronous or basic threading) triggered from the view.
4.  **Status Feedback:** Enhance UI (`submit_url.html`, `views.py`) to show basic feedback (e.g., "Crawl started").
5.  **(Future):** More robust error handling and logging.
6.  **(Future):** Background task queue (Celery/Django-Q) for better scalability.
7.  **(Future):** `robots.txt` respect.
8.  **(Future):** Rate limiting/request delays.
9.  **(Future):** More advanced summarization (AI).

## Known Issues

*   N/A (No code implemented yet).

## Evolution of Decisions

*   **Initial Request:** Create a tool to turn a website into an MCP resource via crawling and storing URLs/summaries in SQLite.
*   **Technology Choice:** Decided to use Django to provide a web UI, as requested by the user.
*   **Summarization/Content:** Decided to start with simple title/meta description extraction in the crawler. The integrated `get_page_content` tool will return raw HTML. Deferred AI summarization. Markdown conversion (previously in Node.js server) is removed.
*   **Crawling Scope:** Decided to limit initial scope to the exact starting domain.
*   **Execution Model:** Decided to start with simple synchronous or threaded execution.
*   **API Filtering:** Added domain and date filtering to the `search_pages` API endpoint (will be used internally by `find_pages` tool).
*   **Architecture (2025-04-17):** Decided to integrate the MCP server logic directly into the Django application using a Python `mcp` package, abandoning the separate Node.js server approach.
*   **Architecture Refinement (2025-04-17):** Migrated from the manual `mcp` package integration to using the `django-mcp` library for simplified ASGI mounting and tool definition via decorators.
