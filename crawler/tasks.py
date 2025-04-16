import requests
import logging
import time
from collections import deque
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from .models import CrawledPage

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define a User-Agent
HEADERS = {
    'User-Agent': 'Web2MCPCrawler/1.0 (+https://github.com/your-repo)' # Replace with actual repo URL later
}

# Define file extensions to ignore
IGNORED_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.zip', '.rar', '.tar', '.gz',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp',
    '.mp3', '.mp4', '.avi', '.mov', '.wmv',
    '.css', '.js',
}

def fetch_html(url):
    """Fetches HTML content for a given URL."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        # Check content type to ensure it's likely HTML
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type:
            logging.warning(f"Skipping non-HTML content at {url} (Content-Type: {content_type})")
            # Return None for content, and the response object for potential inspection
            return None, response

        # Decode content carefully
        response.encoding = response.apparent_encoding # Guess encoding
        # Return both text content and the original response object
        return response.text, response
    except requests.exceptions.Timeout:
        logging.error(f"Timeout fetching {url}")
        return None, None # Return None for both on timeout
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None, None # Return None for both on request error
    except Exception as e:
        logging.error(f"Unexpected error fetching {url}: {e}")
        return None, None # Return None for both on other errors

def parse_and_extract(html_content, url):
    """Parses HTML and extracts title, description, and links."""
    try:
        soup = BeautifulSoup(html_content, 'lxml') # Use lxml for speed if available

        # Extract Title
        title_tag = soup.find('title')
        title = title_tag.string.strip() if title_tag else ''

        # Extract Meta Description
        description_tag = soup.find('meta', attrs={'name': 'description'})
        description = description_tag['content'].strip() if description_tag and 'content' in description_tag.attrs else ''

        # Extract Links
        links = set()
        for a_tag in soup.find_all('a', href=True):
            link = a_tag['href'].strip()
            if link:
                links.add(link)

        return title, description, links
    except Exception as e:
        logging.error(f"Error parsing {url}: {e}")
        return '', '', set()

# Corrected function signature and logic
def filter_and_normalize_links(links, base_domain, current_url, restrict_to_path=False, base_path=None):
    """
    Filters and normalizes extracted links.
    - Resolves relative URLs.
    - Ensures links are HTTP/HTTPS.
    - Ensures links are within the base_domain.
    - Removes fragments (#).
    - Ignores links pointing to files with specific extensions.
    """
    valid_links = set()
    current_parsed = urlparse(current_url)

    for link in links:
        try:
            # Remove fragments
            link = link.split('#')[0]

            # Join relative URLs
            full_url = urljoin(current_url, link)
            parsed_url = urlparse(full_url)

            # 1. Check scheme
            if parsed_url.scheme not in ['http', 'https']:
                continue

            # 2. Check domain
            if parsed_url.netloc != base_domain:
                continue

            # 3. Check file extension
            path = parsed_url.path
            if any(path.lower().endswith(ext) for ext in IGNORED_EXTENSIONS):
                continue

            # 4. Check path restriction (NEW) - Moved inside try block
            if restrict_to_path and base_path is not None:
                # Ensure the link's path starts with the required base path
                if not parsed_url.path.startswith(base_path):
                    continue # Skip this link if path doesn't match

            # If all checks pass, add to valid links - Moved inside try block
            valid_links.add(full_url)

        except Exception as e:
            logging.warning(f"Could not process link '{link}' from {current_url}: {e}")
            continue # Skip this link if any processing error occurs

    return valid_links

def crawl_site(initial_page_id, max_pages=None, max_depth=None, restrict_to_path=False, base_path=None):
    """
    Main function to crawl a website starting from a given initial page ID.
    Optionally restricts crawl to a specific path.
    Updates page statuses throughout the process.
    """
    try:
        # 1. Get the initial page object
        initial_page = CrawledPage.objects.get(pk=initial_page_id)
        start_url = initial_page.url
        base_domain = initial_page.domain

        if not base_domain:
            logging.error(f"Initial page ID {initial_page_id} has no domain ({start_url}). Cannot crawl.")
            initial_page.status = CrawledPage.StatusChoices.FAILED
            initial_page.error_message = "Missing domain information."
            initial_page.save(update_fields=['status', 'error_message'])
            return

        restriction_msg = f" restricted to path '{base_path}'" if restrict_to_path else ""
        logging.info(f"Starting crawl from initial page ID: {initial_page_id} ({start_url}) with max_pages={max_pages} max_depth={max_depth}{restriction_msg}")

        # Update initial page status to PROCESSING
        initial_page.status = CrawledPage.StatusChoices.PROCESSING
        initial_page.error_message = None # Clear previous errors
        initial_page.save(update_fields=['status', 'error_message'])

        queue = deque([(start_url, 0)])  # Store tuples of (url, depth)
        visited = {start_url}
        pages_crawled = 0

    except CrawledPage.DoesNotExist:
        logging.error(f"Cannot start crawl: Initial page with ID {initial_page_id} not found.")
        return
    except Exception as e:
        logging.exception(f"Error initializing crawl for page ID {initial_page_id}: {e}")
        try:
            # Try to mark the initial page as failed if we can fetch it
            page = CrawledPage.objects.get(pk=initial_page_id)
            page.status = CrawledPage.StatusChoices.FAILED
            page.error_message = f"Initialization error: {e}"
            page.save(update_fields=['status', 'error_message'])
        except Exception as db_err:
            logging.error(f"Additionally failed to update status for page ID {initial_page_id} after init error: {db_err}")
        return

    # --- Main Crawl Loop ---
    try:

        while queue: # Loop continues as long as there are URLs to process
            current_url, current_depth = queue.popleft()

            # --- Check Limits ---
            if max_pages is not None and pages_crawled >= max_pages:
                logging.info(f"Reached max_pages limit: {max_pages}. Stopping crawl.")
                break # Exit the while loop
            if max_depth is not None and current_depth > max_depth:
                # Don't process this page, but don't stop the whole crawl
                logging.info(f"Skipping {current_url} - Exceeds max_depth {max_depth}")
                # Mark page as failed? Or just skip? Let's skip for now.
                # We might need a 'SKIPPED' status later.
                continue # Go to next iteration of the while loop

            logging.info(f"Processing: {current_url} (Depth: {current_depth}, Crawled: {pages_crawled})")

            # --- Get DB Record and Update Status ---
            try:
                page = CrawledPage.objects.get(url=current_url, domain=base_domain)
                # Mark as PROCESSING before fetching
                page.status = CrawledPage.StatusChoices.PROCESSING
                page.error_message = None # Clear previous errors
                page.save(update_fields=['status', 'error_message'])
            except CrawledPage.DoesNotExist:
                logging.error(f"DB record inconsistency: {current_url} not found during processing. Skipping.")
                continue # Go to next iteration
            except Exception as db_err:
                logging.error(f"DB Error fetching/updating status for {current_url}: {db_err}")
                continue # Go to next iteration

            # --- Fetch HTML ---
            html_content, response_obj = fetch_html(current_url)
            if html_content is None or response_obj is None:
                page.status = CrawledPage.StatusChoices.FAILED
                page.error_message = "Fetch failed (Timeout or Network Error)"
                page.html_content = None
                page.save(update_fields=['status', 'error_message', 'html_content'])
                continue # Go to next iteration

            # --- Parse and Extract ---
            title, description, links = parse_and_extract(html_content, current_url)

            # --- Update DB Record (Success) ---
            page.title = title[:511] # Use model max_length - 1
            page.summary = description
            page.html_content = html_content
            page.status = CrawledPage.StatusChoices.COMPLETED
            page.error_message = None # Clear error on success
            page.save(update_fields=['title', 'summary', 'status', 'error_message', 'html_content', 'updated_at'])
            logging.info(f"Successfully processed and saved: {current_url}")
            pages_crawled += 1 # Increment only on successful processing

            # --- Filter and Normalize Links ---
            valid_new_links = filter_and_normalize_links(
                links,
                base_domain,
                current_url,
                restrict_to_path=restrict_to_path,
                base_path=base_path
            )

            # --- Add New Links to Queue and DB (Revised Logic) ---
            for link in valid_new_links:
                # 1. Check if already visited in this crawl session
                if link in visited:
                    continue

                # 2. Check depth limit before proceeding
                next_depth = current_depth + 1
                if max_depth is not None and next_depth > max_depth:
                    logging.debug(f"Skipping {link} - Exceeds max_depth {max_depth}")
                    continue # Don't add links that exceed max depth

                # 3. Check page limit before adding to queue/visited
                # Estimate total pages if added: current crawled + current queue size + 1
                if max_pages is not None and (pages_crawled + len(queue) + 1) > max_pages:
                    logging.info(f"Skipping adding {link} to queue - max_pages limit ({max_pages}) would be reached.")
                    # Optionally create/update DB record as PENDING but don't queue or visit?
                    # For now, just skip adding to queue/visited.
                    continue

                # 4. Get or Create DB record and potentially reset status
                try:
                    new_page, created = CrawledPage.objects.get_or_create(
                        url=link,
                        defaults={'domain': base_domain, 'status': CrawledPage.StatusChoices.PENDING}
                    )

                    # If the page existed but wasn't PENDING (e.g., COMPLETED/FAILED from a previous run),
                    # reset it to PENDING for this new crawl.
                    if not created and new_page.status != CrawledPage.StatusChoices.PENDING:
                        logging.debug(f"Resetting existing page {link} to PENDING for re-crawl.")
                        new_page.status = CrawledPage.StatusChoices.PENDING
                        new_page.title = ''
                        new_page.summary = ''
                        new_page.html_content = None # Clear old content
                        new_page.error_message = None # Clear old errors
                        # Note: We don't reset crawled_at, but updated_at will change
                        new_page.save(update_fields=['status', 'title', 'summary', 'html_content', 'error_message', 'updated_at'])

                    # 5. Add to visited set and queue
                    visited.add(link) # Mark as visited for this session
                    queue.append((link, next_depth))
                    logging.debug(f"Added to queue: {link} (Depth: {next_depth})")

                except Exception as db_err:
                    # Handle potential IntegrityError if URL is too long, etc.
                    logging.error(f"DB Error processing record for {link}: {db_err}")
                    # Do not add to visited or queue if DB interaction failed

            # --- Politeness Delay ---
            time.sleep(0.5) # Wait half a second between requests

        # --- End of While Loop ---
        logging.info(f"Crawl loop finished for initial page ID: {initial_page_id} ({start_url}). Crawled {pages_crawled} pages.")

        # Final check: If the initial page is still PROCESSING (e.g., loop finished due to limits before processing it fully), mark as COMPLETED?
        # This depends on the desired final state. Let's assume if the loop finishes without error, it's completed.
        # Re-fetch the initial page to check its final status from the loop.
        final_initial_page = CrawledPage.objects.get(pk=initial_page_id)
        if final_initial_page.status == CrawledPage.StatusChoices.PROCESSING:
             final_initial_page.status = CrawledPage.StatusChoices.COMPLETED
             final_initial_page.save(update_fields=['status'])
             logging.info(f"Marked initial page {initial_page_id} as COMPLETED after crawl loop finished.")

    except Exception as e:
        # --- Global Error Handling for the Crawl ---
        logging.exception(f"Critical error during crawl for initial page ID {initial_page_id} ({start_url}): {e}")
        try:
            # Attempt to mark the initial page as FAILED
            error_page = CrawledPage.objects.get(pk=initial_page_id)
            error_page.status = CrawledPage.StatusChoices.FAILED
            error_page.error_message = f"Runtime error: {e}"
            error_page.save(update_fields=['status', 'error_message'])
        except Exception as db_err:
            logging.error(f"Additionally failed to update status for page ID {initial_page_id} after runtime error: {db_err}")
