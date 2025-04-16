# Project Brief

*This file is the foundation document that shapes all other Memory Bank files. It defines the core requirements and goals of the project and serves as the source of truth for the project scope.*

## Project Goal

The primary goal of this project, named "Web2MCP", is to create a web application using the Django framework. This application will allow users to input a starting website URL. The tool will then crawl accessible pages within the same domain, excluding media, CSS, and JavaScript files. For each valid HTML page found, it will extract the URL, page title, and meta description (as an initial summary). This extracted data will be stored in an SQLite database.

The ultimate purpose of this collected data is to serve as a structured, searchable resource for Model Context Protocol (MCP) agents, enabling them to efficiently find relevant documentation or information URLs from the crawled websites.

## Core Requirements

1.  **Web Interface:** Provide a user-friendly web UI built with Django.
2.  **URL Input:** Allow users to submit a starting URL via the web interface.
3.  **Web Crawler:** Implement a crawler that:
    *   Starts from the given URL.
    *   Recursively finds links within the *same domain*.
    *   Filters out non-HTML content (images, CSS, JS, etc.).
    *   Avoids crawling external domains or subdomains (initially).
4.  **Data Extraction:** Extract the URL, `<title>`, and `<meta name="description">` from each valid page.
5.  **Database Storage:** Store the extracted data (URL, title, summary, domain, timestamp, status) in an SQLite database using Django models.
6.  **Status Tracking:** Provide feedback on the crawling process (e.g., pending, processing, completed, failed).
