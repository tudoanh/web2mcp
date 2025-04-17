# Web2MCP - Website Crawler for MCP

Web2MCP is a Django web application designed to crawl websites, extract key metadata (URL, title, summary), and store it in an SQLite database. The primary goal is to create a structured data source that can be easily queried by Model Context Protocol (MCP) agents to find relevant information within the crawled websites.

![Screenshot](docs/images/screenshot.png)

## Features

*   **Simple Web UI:** Submit a starting URL via a clean web interface.
*   **Same-Domain Crawling:** Crawls pages accessible within the same domain as the starting URL.
*   **Metadata Extraction:** Extracts the page URL, `<title>`, and `<meta name="description">` content.
*   **SQLite Storage:** Stores extracted data efficiently in an SQLite database.
*   **Integrated MCP Server:** Includes an MCP server using `django-mcp` to provide tools for searching and retrieving crawled data.

## Tech Stack

*   **Backend:** Python 3.x, Django 4.x
*   **Database:** SQLite
*   **Libraries:**
    *   `requests` (for fetching URLs)
    *   `BeautifulSoup4` (for HTML parsing)
    *   `lxml` (HTML parser)
    *   `django-mcp` (for MCP server integration)
    *   `uvicorn` (ASGI server)

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd web2mcp
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    # .\venv\Scripts\activate  # Windows
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```
5.  **Run the development server (using ASGI):**
    ```bash
    # Ensure uvicorn is installed via requirements.txt
    uvicorn core.asgi:application --reload --port 8008 
    ```
6.  Access the application at `http://127.0.0.1:8008/` in your browser.

## Development using Docker Compose (Recommended)

This project includes Docker configuration for a consistent development environment using Docker Compose.

**Prerequisites:**
*   Docker installed: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
*   Docker Compose installed (usually included with Docker Desktop): [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)

**Steps:**

1.  **Clone the repository (if not already done):**
    ```bash
    git clone <repository-url>
    cd web2mcp
    ```
2.  **Build and start the services:**
    ```bash
    # This builds and starts the 'web' service defined in docker-compose.yml
    docker-compose up --build -d 
    ```
    *   `--build`: Builds the image if it doesn't exist or if the Dockerfile has changed.
    *   `-d`: Runs the container in detached mode (in the background).
3.  **Apply database migrations (first time or after model changes):**
    Open a separate terminal in the `web2mcp` directory and run:
    ```bash
    docker-compose exec web python manage.py migrate
    ```
4.  **Access the Django application:**
    Open `http://127.0.0.1:8008/` in your browser. The Django application running inside the container includes the integrated MCP server capabilities.
5.  **Connecting MCP Clients:** Configure your MCP client (e.g., VS Code extension) to connect to the running Django application's MCP endpoint, typically exposed via the mapped port (e.g., `http://localhost:8008/mcp` if using HTTP transport, or configure for stdio if needed, though `django-mcp` primarily uses HTTP/WebSocket). Refer to `django-mcp` and your client's documentation.
6.  **View logs:**
    ```bash
    docker-compose logs -f web # Follow logs for the web service
    ```
7.  **Stop the service:**
    ```bash
    docker-compose down
    ```
    *   Use `docker-compose down -v` to also remove the volumes (including the database data if stored in a named volume, though here it's persisted via the bind mount).

## Usage

1.  Navigate to the running application in your web browser.
2.  Enter a valid starting URL (e.g., `https://docs.djangoproject.com/en/4.2/`) into the form.
3.  Click "Submit".
4.  The application will begin crawling the site (currently synchronous or basic threading - see `memory-bank/activeContext.md`). Status updates may be basic in the initial version.
5.  MCP tools (`find_pages`, `get_page_content`) are available via the integrated MCP server endpoint (typically `/mcp`), managed by `django-mcp`.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

This project is licensed under the MIT License.
