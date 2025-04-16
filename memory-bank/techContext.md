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
*   (Potentially a background task runner like `celery` or `django-q` in the future)
*   **MCP Server Dependencies (Node.js):**
    *   `@modelcontextprotocol/sdk`
    *   `axios`
    *   `turndown` (For HTML to Markdown conversion in `get_page_content` tool)
    *   `@types/turndown` (TypeScript types for turndown)

## Technical Constraints

*   **Initial Scope:** Crawling is limited to the same domain as the starting URL. Subdomains and external sites are excluded.
*   **Resource Limits:** Crawling large sites might be resource-intensive (CPU, memory, network). The initial implementation will run synchronously or via a simple background thread, which might not scale well without a proper task queue for very large sites.
*   **Error Handling:** Robust error handling (network issues, parsing errors, invalid HTML) needs to be implemented.
*   **Rate Limiting/Politeness:** The crawler should respect `robots.txt` (future enhancement) and avoid overwhelming the target server (implement delays between requests).
*   **Summarization:** Initial summarization is basic (title/meta description). More advanced summarization (e.g., AI) is a future consideration.

## Tool Usage Patterns

*   Use Django's ORM for all database interactions.
*   Use Django Forms for input validation.
*   Use Django Templates for rendering the UI.
*   Separate crawling logic from view logic, potentially in a `tasks.py` or `utils.py` module within the Django app.
