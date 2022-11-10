from rest_framework.pagination import PageNumberPagination


class PaginateCustom(PageNumberPagination):

    page_size_query_param = 'limit'
