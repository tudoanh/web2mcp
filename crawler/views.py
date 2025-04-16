from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from urllib.parse import urlparse
from django.http import JsonResponse, HttpRequest, HttpResponseBadRequest
from django.db.models import Q # For complex lookups
from datetime import datetime # For date filtering

from .forms import UrlSubmitForm
from .models import CrawledPage
from .tasks import crawl_site # Import the main crawl function
import threading # Import threading

class SubmitUrlView(View):
    """
    View to handle URL submission for crawling.
    """
    template_name = 'crawler/submit_url.html'
    form_class = UrlSubmitForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        # TODO: Add context for listing recent crawls/pages later
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            url_to_crawl = form.cleaned_data['url']
            max_pages = form.cleaned_data.get('max_pages')
            max_depth = form.cleaned_data.get('max_depth')
            restrict_to_path = form.cleaned_data.get('restrict_to_path', False) # Get the checkbox value

            # --- Trigger the crawl ---
            try:
                # Calculate base_path if restriction is enabled
                base_path = None
                parsed_uri = urlparse(url_to_crawl)
                if restrict_to_path:
                    base_path = parsed_uri.path
                    # Ensure base_path ends with '/' if it's not just '/'
                    if base_path != '/' and not base_path.endswith('/'):
                         # This might happen if the input URL is like https://example.com/docs
                         # We might want to treat this as the directory /docs/
                         # For now, let's assume input URLs for path restriction end with /
                         # Or maybe just use the path as is. Let's use it as is for now.
                         pass # Keep base_path as parsed_uri.path

                # 1. Get or create the initial page record
                parsed_uri = urlparse(url_to_crawl)
                domain = parsed_uri.netloc
                page, created = CrawledPage.objects.get_or_create(
                    url=url_to_crawl,
                    defaults={'domain': domain, 'status': CrawledPage.StatusChoices.PENDING}
                )
                # If it already existed, ensure it's marked as pending for this new crawl request
                if not created and page.status != CrawledPage.StatusChoices.PENDING:
                    page.status = CrawledPage.StatusChoices.PENDING
                    # Reset other fields if needed? For now, just status.
                    page.title = ''
                    page.summary = ''
                    page.error_message = None
                    page.save(update_fields=['status', 'title', 'summary', 'error_message', 'updated_at'])

                # 2. Start the crawl function in a background thread
                # NOTE: Using basic threading is simpler for now but less robust than
                # a dedicated task queue like Celery for handling failures, retries, etc.
                crawl_thread = threading.Thread(
                    target=crawl_site,
                    args=(page.id, max_pages, max_depth, restrict_to_path, base_path),
                    # Pass page.id instead of url_to_crawl, assuming crawl_site is updated
                    daemon=True # Allows the main process to exit even if thread is running
                )
                crawl_thread.start()

                success_message = f"Crawl initiated in background for: {url_to_crawl}"
                if restrict_to_path:
                    success_message += f" (restricted to path: {base_path})"
                messages.success(request, _(success_message))

            except Exception as e:
                # Catch potential errors during initial DB interaction or crawl setup
                messages.error(request, _(f"Failed to initiate crawl for {url_to_crawl}: {e}"))
                # Optionally log the exception here
                # logger.exception(f"Failed to initiate crawl for {url_to_crawl}")

            # --- End Trigger ---

            # Re-render the same page, passing the initial page ID for polling
            # Manually create context as base View doesn't have get_context_data
            context = {
                'form': form, # Show the form again (contains submitted data)
                'start_polling_page_id': page.id # Pass ID to template for status polling
            }
            return render(request, self.template_name, context)

        # If form is invalid, re-render the page with the form and errors
        context = {'form': form}
        messages.error(request, _("Please correct the errors below."))
        return render(request, self.template_name, context)

# Make the view available
submit_url_view = SubmitUrlView.as_view()


# --- API Views for MCP Server ---

def search_pages_api(request: HttpRequest):
    """
    API endpoint to search crawled pages by keyword in title or summary.
    Expects a 'keyword' GET parameter.
    Optional GET parameters: 'domain', 'start_date' (YYYY-MM-DD), 'end_date' (YYYY-MM-DD).
    """
    keyword = request.GET.get('keyword')
    domain_filter = request.GET.get('domain')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if not keyword:
        return HttpResponseBadRequest(JsonResponse({'error': "Missing 'keyword' query parameter."}, status=400))

    try:
        # Base filters: keyword search and completed status
        filters = Q(
            Q(title__icontains=keyword) | Q(summary__icontains=keyword),
            status=CrawledPage.StatusChoices.COMPLETED
        )

        # Add optional domain filter
        if domain_filter:
            filters &= Q(domain__iexact=domain_filter) # Case-insensitive domain match

        # Add optional date filters
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                filters &= Q(updated_at__date__gte=start_date) # Filter by date part of updated_at
            except ValueError:
                return HttpResponseBadRequest(JsonResponse({'error': "Invalid 'start_date' format. Use YYYY-MM-DD."}, status=400))

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                filters &= Q(updated_at__date__lte=end_date) # Filter by date part of updated_at
            except ValueError:
                return HttpResponseBadRequest(JsonResponse({'error': "Invalid 'end_date' format. Use YYYY-MM-DD."}, status=400))

        # Apply all filters
        matching_pages = CrawledPage.objects.filter(filters).values(
            'url', 'title', 'summary', 'domain', 'updated_at' # Include domain and timestamp in results
        )

        # Convert datetime objects to ISO format strings for JSON serialization
        results_list = list(matching_pages)
        for page in results_list:
            if isinstance(page.get('updated_at'), datetime):
                page['updated_at'] = page['updated_at'].isoformat()

        return JsonResponse({'results': results_list})

    except Exception as e:
        # Log the error internally if needed
        # logger.error(f"Error during API search: {e}")
        return JsonResponse({'error': 'An internal error occurred during search.'}, status=500)


def get_content_api(request: HttpRequest):
    """
    API endpoint to retrieve the HTML content of a specific crawled page.
    Expects a 'url' GET parameter.
    """
    page_url = request.GET.get('url')
    if not page_url:
        return HttpResponseBadRequest(JsonResponse({'error': "Missing 'url' query parameter."}, status=400))

    try:
        # Use get_object_or_404 for cleaner handling of not found pages
        page = get_object_or_404(CrawledPage, url=page_url, status=CrawledPage.StatusChoices.COMPLETED)

        return JsonResponse({
            'url': page.url,
            'html_content': page.html_content or "" # Return empty string if content is None/null
        })

    except CrawledPage.DoesNotExist:
         # This case is handled by get_object_or_404, but kept for clarity if we change the query
         return JsonResponse({'error': f"Page with URL '{page_url}' not found or not completed."}, status=404)
    except Exception as e:
        # Log the error internally if needed
        # logger.error(f"Error during API content retrieval for URL '{page_url}': {e}")
        return JsonResponse({'error': 'An internal error occurred while retrieving content.'}, status=500)


# --- API View for Crawl Status ---

from django.db.models import Count

def crawl_status_api(request: HttpRequest, page_id: int):
    """
    API endpoint to get the status of a crawl job, identified by the ID
    of the initial page submitted. Returns summary statistics.
    """
    try:
        # Get the initial page that started this conceptual "job"
        initial_page = get_object_or_404(CrawledPage, pk=page_id)
        domain = initial_page.domain

        # Query related pages for the same domain initiated around the same time
        # This assumes pages from the same crawl job share the domain and were created
        # at or after the initial page. This might need refinement if jobs overlap heavily.
        pages_in_job = CrawledPage.objects.filter(
            domain=domain,
            crawled_at__gte=initial_page.crawled_at # Filter by creation time
        )

        # Calculate counts for each status
        status_counts = pages_in_job.values('status').annotate(count=Count('id')).order_by('status')
        total_pages = pages_in_job.count()

        # Determine if any pages are still actively being processed or pending
        is_processing = pages_in_job.filter(
            status__in=[CrawledPage.StatusChoices.PENDING, CrawledPage.StatusChoices.PROCESSING]
        ).exists()

        # Determine an overall status for the UI display
        # If anything is still processing/pending, the job is 'PROCESSING'
        # Otherwise, if the initial page failed, the job is 'FAILED'
        # Otherwise, it's 'COMPLETED' (assuming the initial page completed)
        overall_status = initial_page.status # Start with the initial page's status
        if is_processing:
            overall_status = CrawledPage.StatusChoices.PROCESSING
        elif initial_page.status == CrawledPage.StatusChoices.FAILED:
             overall_status = CrawledPage.StatusChoices.FAILED
        elif not is_processing and initial_page.status == CrawledPage.StatusChoices.COMPLETED:
             # Only truly completed if nothing else is pending/processing
             overall_status = CrawledPage.StatusChoices.COMPLETED
        # Note: This logic might need adjustment based on how the background task signals completion.

        data = {
            'initial_page_id': initial_page.id,
            'initial_page_status': initial_page.status,
            'overall_status': overall_status,
            'total_pages_found': total_pages,
            'status_breakdown': list(status_counts), # e.g., [{'status': 'completed', 'count': 5}, ...]
            'is_processing': is_processing, # Explicit flag for JS to know when to stop polling
            'error_message': initial_page.error_message if initial_page.status == CrawledPage.StatusChoices.FAILED else None,
        }
        return JsonResponse(data)

    except CrawledPage.DoesNotExist:
        return JsonResponse({'error': f'Crawl job with initial page ID {page_id} not found.'}, status=404)
    except Exception as e:
         # Log the error e
         # logger.exception(f"Error in crawl_status_api for page_id {page_id}: {e}")
         return JsonResponse({'error': 'An internal error occurred while fetching crawl status.'}, status=500)
