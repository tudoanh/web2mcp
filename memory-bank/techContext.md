# Tech Context

*This file outlines the technologies used, development setup, technical constraints, dependencies, and tool usage patterns.*

## Core Technologies

*   **Language:** Python 3.x
*   **Web Framework:** Django 4.x (or latest stable)
*   **Database:** SQLite (default for Django, suitable for initial development)
*   **HTTP Requests:** `requests` library
*   **HTML Parsing:** `BeautifulSoup4` library
*   **Environment Management:** (Assumed) Python virtual environment (e.g., `venv`)

## Development Setup

1.  **Clone Repository:** (Assumed the project is in a Git repository)
2.  **Create Virtual Environment:** `python -m venv venv`
3.  **Activate Virtual Environment:** `source venv/bin/activate` (Linux/macOS) or `.\venv\Scripts\activate` (Windows)
4.  **Install Dependencies:** `pip install -r requirements.txt` (A `requirements.txt` file will need to be created and maintained)
5.  **Run Migrations:** `python manage.py migrate`
6.  **Start Development Server:** `python manage.py runserver`
7.  **Access Application:** Open `http://127.0.0.1:8000/` in a web browser.

## Key Dependencies (to be included in `requirements.txt`)

*   `django`
*   `requests`
*   `beautifulsoup4`
*   `lxml` (Often used as a faster parser with BeautifulSoup)
*   `django-mcp` (Library for integrating MCP servers into Django via ASGI)
*   `uvicorn` (ASGI server, needed to run the application)
*   (Potentially a background task runner like `celery` or `django-q` in the future)

## Technical Constraints

*   **Initial Scope:** Crawling is limited to the same domain as the starting URL. Subdomains and external sites are excluded.
*   **Resource Limits:** Crawling large sites might be resource-intensive (CPU, memory, network). The initial implementation will run synchronously or via a simple background thread, which might not scale well without a proper task queue for very large sites.
*   **Error Handling:** Robust error handling (network issues, parsing errors, invalid HTML) needs to be implemented.
*   **Rate Limiting/Politeness:** The crawler should respect `robots.txt` (future enhancement) and avoid overwhelming the target server (implement delays between requests).
*   **Summarization:** Initial summarization is basic (title/meta description). More advanced summarization (e.g., AI) is a future consideration.

## Tool Usage Patterns

*   Use Django's ORM for all database interactions (`crawler` and `mcp_server` apps).
*   Use Django Forms for input validation (`crawler` app).
*   Use Django Templates for rendering the UI (`crawler` app).
*   Separate crawling logic into `crawler/tasks.py`.
*   Implement MCP tools as decorated functions in `mcp_server/tools.py` using `django-mcp`.
*   Mount the MCP server in `core/asgi.py` using `django-mcp`.
*   Ensure tool discovery via `mcp_server/apps.py`.
