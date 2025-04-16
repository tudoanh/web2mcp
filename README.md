# Web2MCP - Website Crawler for MCP

Web2MCP is a Django web application designed to crawl websites, extract key metadata (URL, title, summary), and store it in an SQLite database. The primary goal is to create a structured data source that can be easily queried by Model Context Protocol (MCP) agents to find relevant information within the crawled websites.

![Screenshot](docs/images/screenshot.png)

## Features

*   **Simple Web UI:** Submit a starting URL via a clean web interface.
*   **Same-Domain Crawling:** Crawls pages accessible within the same domain as the starting URL.
*   **Metadata Extraction:** Extracts the page URL, `<title>`, and `<meta name="description">` content.
*   **SQLite Storage:** Stores extracted data efficiently in an SQLite database.
*   **API for MCP:** Provides API endpoints for MCP servers to search crawled pages and retrieve content.

## Tech Stack

*   **Backend:** Python 3.x, Django 4.x
*   **Database:** SQLite
*   **Libraries:**
    *   `requests` (for fetching URLs)
    *   `BeautifulSoup4` (for HTML parsing)
    *   `lxml` (HTML parser)

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
5.  **Run the development server:**
    ```bash
    python manage.py runserver 8008 # Or your preferred port
    ```
6.  Access the application at `http://127.0.0.1:8008/` in your browser.

## Usage

1.  Navigate to the running application in your web browser.
2.  Enter a valid starting URL (e.g., `https://docs.djangoproject.com/en/4.2/`) into the form.
3.  Click "Submit".
4.  The application will begin crawling the site (currently synchronous or basic threading - see `activeContext.md`). Status updates may be basic in the initial version.

## API Endpoints (for MCP Server)

The application exposes the following endpoints for use by the `web2mcp-server` or other MCP clients:

*   `GET /api/search_pages/`: Search crawled pages.
    *   Query Parameters:
        *   `keyword` (required): Search term for title/summary.
        *   `domain` (optional): Filter by domain.
        *   `start_date` (optional, YYYY-MM-DD): Filter by minimum update date.
        *   `end_date` (optional, YYYY-MM-DD): Filter by maximum update date.
*   `GET /api/get_content/`: Retrieve the stored raw HTML content for a specific URL.
    *   Query Parameters:
        *   `url` (required): The exact URL of the page.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

This project is licensed under the MIT License.
