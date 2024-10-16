# ruff: noqa: ERA001
# We are keeping the comments here to show what is removed from parent implementation

from django.core.paginator import InvalidPage
from django.core.paginator import Page as DefaultPage
from django.core.paginator import Paginator as DefaultPaginator
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from drf_kit.pagination.custom_pagination import CustomPagePagination


class LightPage(DefaultPage):
    def has_next(self):
        return len(self.object_list) >= self.paginator.per_page


class LightPaginator(DefaultPaginator):
    def validate_number(self, number):
        try:
            value = int(number)
        except ValueError:
            value = 0
        return max(value, 0)

    def page(self, number):
        """Return a Page object for the given 1-based page number."""
        number = self.validate_number(number)
        bottom: int = (number - 1) * self.per_page
        top: int = bottom + self.per_page
        # if top + self.orphans >= self.count:
        #     top = self.count
        return LightPage(self.object_list[bottom:top], number, self)

    @property
    def count(self):
        raise NotImplementedError()


class LightPagePagination(CustomPagePagination):
    django_paginator_class = LightPaginator

    def get_paginated_response(self, data):
        return Response(
            {
                # 'count': self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )

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

        if self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)
