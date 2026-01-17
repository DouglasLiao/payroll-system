from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class that allows client to control page size.
    
    Query parameters:
    - page: page number (default: 1)
    - page_size: number of items per page (default: 10, max: 100)
    
    Example: /api/payrolls/?page=2&page_size=25
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
