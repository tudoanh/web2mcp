# Active Context

*This file tracks the current focus of work. It includes recent changes, immediate next steps, active decisions, important patterns/preferences discovered, and key learnings.*

## Current Focus

The primary focus is implementing the core crawling logic within the Django application (`crawler/tasks.py`). Additionally, ensuring the MCP server correctly interacts with the enhanced Django API.

## Recent Changes (as of 2025-04-16 10:36 PM)

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
*   **Enhanced MCP Server (`web2mcp-server/src/index.ts`):**
    *   Added `turndown` dependency for HTML-to-Markdown conversion.
    *   Updated `find_pages` tool schema and handler to support `domain`, `start_date`, `end_date` filters and pass them to the Django API.
    *   Updated `get_page_content` tool schema and handler to convert fetched HTML content to Markdown using `turndown` before returning it.

## Immediate Next Steps

1.  **Implement Core Crawler Logic:** Create functions in `crawler/tasks.py` (or `utils.py`) for:
    *   Fetching URL content (`requests`).
    *   Parsing HTML (`BeautifulSoup4`).
    *   Extracting title and meta description.
    *   Extracting valid internal links (same domain, HTML content).
2.  **Integrate Crawler Trigger:** Modify `crawler/views.py` (`SubmitUrlView.post`) to:
    *   Create an initial `CrawledPage` record for the submitted URL.
    *   Call the main crawling function (initially synchronously or using basic threading).
3.  **Database Updates:** Ensure the crawler logic updates `CrawledPage` records with extracted data (title, summary) and status (`completed`, `failed`).
4.  **Basic Status Display:** Enhance the `submit_url.html` template or create a new view/template to show the status of recent crawls or list crawled pages for a domain.
5.  **Error Handling:** Add basic try/except blocks in the crawler logic for network/parsing errors.

## Active Decisions & Considerations

*   **Crawling Execution:** Start with synchronous execution or simple threading triggered from the view. Evaluate the need for a dedicated task queue (Celery/Django-Q) after the basic functionality is working.
*   **Summarization:** Use `<title>` and `<meta name="description">` for the Django crawler. The MCP server's `get_page_content` now returns Markdown.
*   **Scope:** Strictly same-domain crawling for the Django app.
*   **Error Handling:** Implement basic error handling during crawling (e.g., network errors, request timeouts) and log issues. More robust handling can be added later. MCP server has basic API error handling.
*   **UI:** Keep the initial UI very simple (form + basic status feedback).
*   **MCP Server Interaction:** The server now correctly calls the enhanced Django API endpoints and processes the results (filtering, Markdown conversion).

## Important Patterns & Preferences

*   Follow standard Django project structure and best practices.
*   Keep crawling logic separate from view logic.
*   Use Django ORM for database interactions.
*   Maintain clear documentation in the Memory Bank.

## Learnings & Insights

*   The project requires integrating web scraping techniques within a web framework context.
*   Managing the state and potential long-running nature of the crawling process is a key challenge.
