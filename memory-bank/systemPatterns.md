# System Patterns

*This file documents the system architecture, key technical decisions, design patterns in use, component relationships, and critical implementation paths.*

## Architecture Overview

The application follows a standard Django Model-View-Template (MTV) architecture. It will consist of a single core Django app (initially named `crawler`) responsible for handling the crawling logic and data storage.

```mermaid
graph TD
    subgraph User Interaction
        User[User Browser] -- HTTP Request --> SubmitView[submit_url_view]
        SubmitView -- Renders --> Template[HTML Template (Input Form)]
        Template -- Submits Form --> SubmitView
        SubmitView -- Validates --> UrlForm[UrlSubmitForm]
        SubmitView -- Triggers --> CrawlerTask[Crawling Logic (tasks.py)]
    end

    subgraph Crawler Process
        CrawlerTask -- Uses --> Requests[Requests Library]
        CrawlerTask -- Uses --> BeautifulSoup[BeautifulSoup4 Library]
        Requests -- Fetches HTML --> TargetSite[Target Website]
        BeautifulSoup -- Parses HTML --> CrawlerTask
        CrawlerTask -- Interacts with --> ORM[Django ORM]
    end

    subgraph MCP Server Interaction
        MCPServer[web2mcp-server (Node.js)] -- GET /api/search_pages/?... --> SearchAPI[search_pages_api]
        MCPServer -- GET /api/get_content/?... --> GetContentAPI[get_content_api]
        SearchAPI -- Returns JSON --> MCPServer
        GetContentAPI -- Returns JSON (HTML) --> MCPServer
        MCPServer -- Processes (Turndown) --> MCPServer
        MCPServer -- Returns JSON/Markdown --> MCPClient[MCP Client]
    end

    subgraph Django Application (Web2MCP)
        direction LR
        SubmitView
        SearchAPI
        GetContentAPI
        UrlForm
        ORM
        CrawlerTask
    end

    ORM -- Reads/Writes --> DB[(SQLite Database)]

    %% Links showing data flow
    SubmitView -- Interacts with --> ORM
    SearchAPI -- Interacts with --> ORM
    GetContentAPI -- Interacts with --> ORM

```

## Key Components

1.  **`crawler` App:** The main Django application containing models, views, forms, templates, and crawling logic.
2.  **Models (`models.py`):**
    *   `CrawledPage`: Stores information about each discovered URL (URL, title, summary, domain, status, timestamp).
    *   (Potentially) `CrawlJob`: Represents a single crawl task initiated by the user (start URL, status, start/end time). This could help manage multiple crawls.
3.  **Views (`views.py`):**
    *   `submit_url_view`: Handles GET requests to display the URL submission form and potentially a list of recent jobs/pages. Handles POST requests to validate the form and initiate a crawl (currently synchronous).
    *   `search_pages_api`: API endpoint (GET) for the MCP server. Expects `keyword` query parameter. Optionally accepts `domain`, `start_date` (YYYY-MM-DD), `end_date` (YYYY-MM-DD) for filtering. Returns JSON list of matching pages (`url`, `title`, `summary`, `domain`, `updated_at`).
    *   `get_content_api`: API endpoint (GET) for the MCP server. Expects `url` query parameter. Returns JSON with the raw `html_content` of the requested page.
    *   (Potentially) `crawl_status_view`: An API endpoint or view to check the status of an ongoing crawl (for future AJAX updates).
4.  **Forms (`forms.py`):**
    *   `UrlSubmitForm`: Validates the user-submitted starting URL, max pages, max depth, and path restriction option.
5.  **Crawling Logic (`tasks.py` or `utils.py`):**
    *   Contains functions for fetching URLs, parsing HTML, extracting relevant data (title, meta description, links), filtering links (same domain, avoid media/css/js), managing the queue of URLs to visit for a specific job, and updating the database via the ORM.
6.  **Templates (`templates/crawler/`):**
    *   HTML files to render the UI (input form, status display).
7.  **Database (SQLite):** Stores the state of crawl jobs and the discovered page data.

## Design Decisions

*   **Synchronous vs. Asynchronous Crawling:** Initially, the crawling process might be triggered synchronously within the POST request handler or using a simple Python `threading` approach for basic background execution. **Decision:** Start simple (synchronous or basic threading) and introduce a proper task queue (Celery, Django-Q) later if performance becomes an issue for larger sites.
*   **Data Storage:** Use Django's ORM with SQLite for simplicity initially. Can migrate to PostgreSQL or other databases if needed later.
*   **Link Discovery:** Use BeautifulSoup to parse HTML and find `<a>` tags. Filter `href` attributes based on domain and file extension rules.
*   **State Management:** Use the `status` field in the `CrawledPage` or `CrawlJob` model to track progress.

## Critical Implementation Paths

1.  Setting up the Django project structure and the `crawler` app.
2.  Defining the `CrawledPage` model and running initial migrations.
3.  Creating the URL submission form and view.
4.  Implementing the basic HTML fetching and parsing logic.
5.  Implementing the link extraction and filtering logic.
6.  Integrating the crawling logic with the view (initially synchronous/threaded).
7.  Storing extracted data in the database.
8.  Creating basic templates to display the form and feedback.
