# Product Context

*This file describes the "why" behind the project. What problems does it solve? How should it work from a user's perspective? What are the key user experience goals?*

## Problem Solved

Accessing specific information within large websites, especially documentation sites, can be time-consuming. Standard search engines might not index deeply or provide the context needed by specialized agents (like MCP agents). This tool aims to bridge that gap by creating a focused, structured index of a website's content, specifically tailored for programmatic access. By crawling a site and storing summarized content mapped to URLs, it enables agents to quickly query and retrieve relevant page links based on content summaries, rather than navigating the site manually or relying on general-purpose search.

## User Experience Goals

1.  **Simplicity:** The primary user interaction should be straightforward: paste a URL and click "Crawl".
2.  **Transparency:** The user should be able to see the status of the crawl (e.g., starting, in progress, number of pages found, completed, errors).
3.  **Feedback:** Provide clear feedback on success or failure of the crawl initiation.
4.  **Accessibility (for Agents):** The resulting database should be easily queryable by MCP agents (though the specific agent interaction mechanism is outside the initial scope of this UI tool).

## How It Should Work (User Perspective)

1.  The user navigates to the Web2MCP web application.
2.  They are presented with a simple form field to enter a starting URL.
3.  Upon submitting the URL, the application validates it and initiates the crawling process in the background.
4.  The UI updates to show the crawl job has started, possibly displaying the domain being crawled and its status ('Pending' or 'Processing').
5.  (Optional/Future Enhancement) The UI could show a list of recently crawled sites or allow viewing the pages found for a specific crawl job.
6.  The core output (the SQLite database) is primarily intended for backend/agent use, not direct user browsing through this initial UI.
