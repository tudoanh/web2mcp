# System Patterns

*This file documents the system architecture, key technical decisions, design patterns in use, component relationships, and critical implementation paths.*

## Architecture Overview

The application follows a standard Django Model-View-Template (MTV) architecture. It consists of a `crawler` app for web crawling and data storage, and an `mcp_server` app to handle interactions with MCP clients.

```mermaid
graph TD
    subgraph User Interaction
        User[User Browser] -- HTTP Request --> SubmitView[crawler.views.submit_url_view]
        SubmitView -- Renders --> Template[HTML Template (Input Form)]
        Template -- Submits Form --> SubmitView
        SubmitView -- Validates --> UrlForm[crawler.forms.UrlSubmitForm]
        SubmitView -- Triggers --> CrawlerTask[crawler.tasks.Crawling Logic]
    end

    subgraph Crawler Process
        CrawlerTask -- Uses --> Requests[Requests Library]
        CrawlerTask -- Uses --> BeautifulSoup[BeautifulSoup4 Library]
        Requests -- Fetches HTML --> TargetSite[Target Website]
        BeautifulSoup -- Parses HTML --> CrawlerTask
        CrawlerTask -- Interacts with --> ORM[Django ORM]
    end

    subgraph MCP Interaction (django-mcp)
        MCPClient[MCP Client] -- MCP Request --> ASGIMount[ASGI Mount (/mcp)]
        ASGIMount -- Handled by --> DjangoMCP[django-mcp Library]
        DjangoMCP -- Discovers/Executes --> ToolLogic[mcp_server.tools (Decorated Functions)]
        ToolLogic -- Interacts with --> ORM
        DjangoMCP -- Formats Response --> MCPClient
    end

    subgraph Django Application (Web2MCP)
        direction LR
        crawler.views.SubmitView
        crawler.forms.UrlSubmitForm
        ORM
        crawler.tasks.CrawlerTask
        ToolLogic
    end

    ORM -- Reads/Writes --> DB[(SQLite Database)]

    %% Links showing data flow
    SubmitView -- Interacts with --> ORM
    ToolLogic -- Reads --> ORM
```

## Key Components

1.  **`crawler` App:** Contains models, views, forms, templates, and logic related to the web crawling functionality.
    *   **Models (`crawler/models.py`):**
        *   `CrawledPage`: Stores information about each discovered URL (URL, title, summary, domain, status, timestamp, html_content).
        *   (Potentially) `CrawlJob`: Represents a single crawl task.
    *   **Views (`crawler/views.py`):**
        *   `submit_url_view`: Handles the user-facing URL submission form and initiates crawls.
        *   (Potentially) `crawl_status_view`: Checks crawl status.
    *   **Forms (`crawler/forms.py`):**
        *   `UrlSubmitForm`: Validates user input for crawling.
    *   **Crawling Logic (`crawler/tasks.py`):**
        *   Functions for fetching, parsing, extracting, filtering, and storing crawled data.
    *   **Templates (`crawler/templates/crawler/`):**
        *   HTML for the user interface.
2.  **`mcp_server` App:** Defines MCP tools and resources.
    *   **Tool Logic (`mcp_server/tools.py`):**
        *   Contains functions decorated with `@mcp.tool()` or `@mcp.resource()` from `django_mcp`.
        *   `find_pages`: Implements the logic to search `CrawledPage` records based on keywords.
        *   `get_page_content`: Implements the logic to retrieve `html_content` for a specific URL from `CrawledPage`.
    *   **App Config (`mcp_server/apps.py`):**
        *   Imports `mcp_server.tools` in its `ready()` method to ensure tool discovery by `django-mcp`.
    *   **(No Views/URLs):** Request handling and routing are managed by `django-mcp` via the ASGI mount point.
3.  **Database (SQLite):** Shared database storing `CrawledPage` data accessed by both apps.
4.  **ASGI Configuration (`core/asgi.py`):**
    *   Uses `mount_mcp_server` from `django_mcp` to wrap the main Django application and handle requests to the `/mcp` path.

## Design Decisions

*   **MCP Integration:** MCP server functionality is integrated using the `django-mcp` library. This library handles request parsing, tool dispatching, and response formatting via ASGI mounting (`core/asgi.py`) and tool decorators (`mcp_server/tools.py`).
*   **Synchronous vs. Asynchronous Crawling:** Crawling initiated via the UI will start simple (synchronous or basic threading) and can be enhanced with a task queue (Celery, Django-Q) later if needed. `django-mcp` supports async tool functions if needed.
*   **Data Storage:** Use Django's ORM with SQLite initially.
*   **Link Discovery:** Use BeautifulSoup to parse HTML and find `<a>` tags, filtering based on domain and content type rules.
*   **State Management:** Use the `status` field in the `CrawledPage` model to track progress.

## Critical Implementation Paths

1.  Setting up the Django project structure and the `crawler` app.
2.  Defining the `CrawledPage` model (including `html_content`) and running migrations.
3.  Creating the URL submission form and view (`crawler` app).
4.  Implementing the core crawling logic (`crawler/tasks.py`).
5.  Storing extracted data, including full HTML, in the database.
6.  Creating the `mcp_server` app structure and adding it to `INSTALLED_APPS`.
7.  Adding the `django-mcp` dependency to `requirements.txt`.
8.  Configuring `core/asgi.py` using `mount_mcp_server`.
9.  Implementing the `find_pages` and `get_page_content` tool logic in `mcp_server/tools.py` using `@mcp.tool()` decorators.
10. Ensuring tool discovery by importing `mcp_server.tools` in `mcp_server/apps.py`.
