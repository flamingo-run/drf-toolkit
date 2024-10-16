from django.core.paginator import InvalidPage
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination, _get_displayed_page_numbers, _get_page_links
from rest_framework.utils.urls import remove_query_param, replace_query_param


class CustomPagePagination(PageNumberPagination):
    page_size_query_param = "page_size"
    page_start = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page = None
        self.request = None

    @property
    def _shift(self):
        return 1 - self.page_start

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, self.page_start)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(int(page_number) + self._shift)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number,
                message=str(exc),
            )
            raise NotFound(msg) from exc

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.previous_page_number()
        if page_number == self.page_start:
            return remove_query_param(url, self.page_query_param)
        return replace_query_param(url, self.page_query_param, page_number)

    def get_next_link(self):
        if not self.page.has_next():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.next_page_number()
        return replace_query_param(url, self.page_query_param, page_number)

    def get_html_context(self):
        base_url = self.request.build_absolute_uri()

        def page_number_to_url(page_number):
            if page_number == self.page_start:
                return remove_query_param(base_url, self.page_query_param)
            return replace_query_param(base_url, self.page_query_param, page_number)

        current = self.page.number
        final = self.page.paginator.num_pages
        page_numbers = _get_displayed_page_numbers(current, final)
        page_links = _get_page_links(page_numbers, current, page_number_to_url)

        return {"previous_url": self.get_previous_link(), "next_url": self.get_next_link(), "page_links": page_links}
