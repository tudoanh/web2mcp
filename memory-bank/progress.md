# Progress

*This file tracks what works, what's left to build, the current status, known issues, and the evolution of project decisions.*

## Current Status (as of 2025-04-16 11:45 AM)

*   **Phase:** Initial Implementation (UI, Structure, API, MCP Server Enhancements).
*   **Overall Progress:** Project planned, Memory Bank initialized. Core Django structure for the `crawler` app is set up (model, migrations, basic form, view, template, URL routing). Django API endpoints (`/api/search_pages/`, `/api/get_content/`) are implemented. The MCP server (`web2mcp-server`) is functional and enhanced. Dependencies are listed in `requirements.txt`. The application can run, display the form, accept URL submissions (but doesn't crawl yet), and the MCP server can interact with the enhanced API.

## What Works

*   Django project runs (`python manage.py runserver`).
*   The `crawler` app is registered.
*   Database migrations for `CrawledPage` model are applied.
*   The URL submission form is displayed at the root URL (`/`).
*   The form validates input URL format (HTTP/HTTPS).
*   Submitting a valid URL shows a success message (placeholder action).
*   Submitting an invalid URL shows form errors.
*   **Django API (`/api/search_pages/`):**
    *   Accepts `keyword` parameter.
    *   Accepts optional `domain`, `start_date`, `end_date` parameters for filtering.
    *   Returns JSON results including `url`, `title`, `summary`, `domain`, `updated_at`.
*   **Django API (`/api/get_content/`):**
    *   Accepts `url` parameter.
    *   Returns JSON with `url` and `html_content`.
*   **MCP Server (`web2mcp-server`):**
    *   `find_pages` tool: Accepts `keyword` and optional filters, calls Django API, returns JSON results.
    *   `get_page_content` tool: Accepts `url`, calls Django API, converts HTML to Markdown using `turndown`, returns Markdown text.

## What's Left to Build (High-Level)

1.  **Crawling Engine (`crawler/tasks.py` or `utils.py`):**
    *   Implement URL fetching (`requests`) with error handling (timeouts, status codes).
    *   Implement HTML parsing (`BeautifulSoup4`).
    *   Implement data extraction (title, meta description).
    *   Implement link extraction and filtering (same domain, HTML content check, avoid media/css/js).
    *   Manage visited URLs to prevent re-crawling and loops.
2.  **Crawler Integration (`crawler/views.py`):**
    *   Connect the `SubmitUrlView` POST handler to trigger the crawl process.
    *   Create/update `CrawledPage` records in the database with status and extracted data.
3.  **Process Management:** Decide on and implement initial crawl execution (synchronous or basic threading).
4.  **Status Feedback:** Enhance UI to show crawl progress/results.
5.  **(Future):** Robust error handling and logging.
6.  **(Future):** Background task queue (Celery/Django-Q).
7.  **(Future):** `robots.txt` respect.
8.  **(Future):** Rate limiting/request delays.
9.  **(Future):** More advanced summarization (AI).
10. **(Future):** Agent query interface/API.

## Known Issues

*   N/A (No code implemented yet).

## Evolution of Decisions

*   **Initial Request:** Create a tool to turn a website into an MCP resource via crawling and storing URLs/summaries in SQLite.
*   **Technology Choice:** Decided to use Django to provide a web UI, as requested by the user.
*   **Summarization/Content:** Decided to start with simple title/meta description extraction in the crawler. The MCP server's `get_page_content` tool now provides content as Markdown. Deferred AI summarization.
*   **Crawling Scope:** Decided to limit initial scope to the exact starting domain.
*   **Execution Model:** Decided to start with simple synchronous or threaded execution, deferring complex background task queues.
*   **API Filtering:** Added domain and date filtering to the `search_pages` API endpoint based on user request.
