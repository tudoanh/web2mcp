# Active Context

*This file tracks the current focus of work. It includes recent changes, immediate next steps, active decisions, important patterns/preferences discovered, and key learnings.*

## Current Focus

The primary focus is implementing the core crawling logic within the `crawler` app (`crawler/tasks.py`) and integrating it with the `crawler` view. The MCP server functionality has been successfully migrated to use the `django-mcp` library.

## Recent Changes (as of 2025-04-17 10:31 AM)

*   Created `README.md` with project description, setup instructions, usage, and a screenshot (`docs/images/screenshot.png`).
*   Project goal defined: Create a Django-based web crawler (Web2MCP) to index websites for MCP agent use.
*   Technology stack chosen: Python, Django, SQLite, Requests, BeautifulSoup4.
*   Initial architecture planned: Standard Django MTV pattern with a dedicated `crawler` app.
*   Core Memory Bank files (`projectbrief.md`, `productContext.md`, `techContext.md`, `systemPatterns.md`, `activeContext.md`, `progress.md`) populated with initial project details and plans.
*   Created `requirements.txt`.
*   Created `crawler` Django app.
*   Defined `CrawledPage` model and applied migrations.
*   Added `crawler` to `INSTALLED_APPS`.
*   Implemented basic `UrlSubmitForm`, `submit_url_view`, and `submit_url.html` template.
*   Configured URL routing for the `crawler` app, including API endpoints `/api/search_pages/` and `/api/get_content/`.
*   **Enhanced Django API (`crawler/views.py`):**
    *   Updated `search_pages_api` to accept optional `domain`, `start_date`, and `end_date` query parameters for filtering search results.
*   **Architectural Shift Decision (2025-04-17):** Decided to integrate MCP server logic directly into the Django application using a Python `mcp` package, instead of using the separate Node.js server. This required creating a new `mcp_server` Django app.
*   **Migration to `django-mcp` (2025-04-17):**
    *   Replaced `mcp` dependency with `django-mcp` in `requirements.txt`.
    *   Updated `core/asgi.py` to use `mount_mcp_server` from `django-mcp`.
    *   Refactored `mcp_server/tools.py` to use `@mcp.tool()` decorators from `django-mcp`.
    *   Configured tool discovery in `mcp_server/apps.py`.
    *   Removed redundant `mcp_server/views.py`, `mcp_server/urls.py`, and `mcp_server/server.py`.
    *   Updated Memory Bank files (`systemPatterns.md`, `techContext.md`) to reflect the new architecture.

## Immediate Next Steps

1.  **Implement Core Crawler Logic:** Implement functions in `crawler/tasks.py` for fetching, parsing, extracting, and storing data (including full HTML content).
2.  **Integrate Crawler Trigger:** Modify `crawler/views.py` (`submit_url_view`) to call the crawling logic from `crawler/tasks.py`.
3.  **Error Handling:** Add basic error handling in crawler logic (`crawler/tasks.py`).
4.  **Status Feedback:** Enhance UI (`crawler/templates/crawler/submit_url.html` and potentially `crawler/views.py`) to show basic crawl status (e.g., "Crawling started for [domain]").
5.  **Update Memory Bank:** Finalize updates to `activeContext.md` and `progress.md`.

## Active Decisions & Considerations

*   **Architecture:** MCP server functionality is integrated using the `django-mcp` library via ASGI mounting and tool decorators. The `mcp_server` app now primarily holds the tool definitions.
*   **Crawling Execution:** Start with synchronous/threaded execution triggered directly from the `crawler` view. Task queue is a future enhancement.
*   **Data Storage:** `CrawledPage` model needs to store the full `html_content`.
*   **Summarization:** Initial summarization in `CrawledPage` uses title/meta description. The `get_page_content` MCP tool will return the stored raw HTML. (Markdown conversion is removed as the `turndown` dependency was in the Node.js server).
*   **Scope:** Strictly same-domain crawling.
*   **Error Handling:** Implement basic error handling during crawling and in MCP tool execution.
*   **UI:** Keep the `crawler` UI simple.

## Important Patterns & Preferences

*   Follow standard Django project structure and best practices.
*   Separate concerns between apps (`crawler` for crawling/UI, `mcp_server` for MCP tool definitions).
*   Keep core logic (crawling in `tasks.py`, tool implementation in `tools.py`) separate from view logic.
*   Use Django ORM for all database interactions.
*   Utilize `django-mcp` for handling MCP server mechanics (request/response, routing, discovery).
*   Maintain clear documentation in the Memory Bank, reflecting current architecture and decisions.

## Learnings & Insights

*   Architectural flexibility is important; adapting the plan based on available tools (`mcp` package vs. `django-mcp`) can simplify the overall system.
*   Using `django-mcp` significantly reduces the boilerplate code needed for MCP integration compared to manual implementation with the base `mcp` package and ASGI frameworks like Starlette.
*   Integrating MCP server logic directly into Django requires careful app structure and dependency management, especially ensuring tools are discovered correctly (`apps.py`).
*   The project requires integrating web scraping techniques within a web framework context.
*   Managing the state and potential long-running nature of the crawling process remains a key challenge (addressed next by implementing the crawler logic).
