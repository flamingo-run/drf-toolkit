from datetime import timedelta
from wsgiref import handlers

from django.http import HttpResponse
from django.utils.timezone import now
from rest_framework_extensions.cache import decorators
from rest_framework_extensions.key_constructor import bits
from rest_framework_extensions.key_constructor.constructors import KeyConstructor


class QueryListParamsKeyBit(bits.AllArgsMixin, bits.KeyBitDictBase):
    def get_source_dict(self, params, view_instance, view_method, request, args, kwargs):
        data = {k: request.query_params.getlist(k) for k in request.GET}
        data["renderer_type"] = request.accepted_media_type
        return data


class CacheKeyConstructor(KeyConstructor):
    unique_view_id = bits.UniqueMethodIdKeyBit()
    args = bits.ArgsKeyBit()
    kwargs = bits.KwargsKeyBit()
    all_query_params = QueryListParamsKeyBit()


cache_key_constructor = CacheKeyConstructor()


class BodyKeyBit(bits.AllArgsMixin, bits.KeyBitDictBase):
    def get_source_dict(self, params, view_instance, view_method, request, args, kwargs):
        return request.POST


class BodyCacheKeyConstructor(CacheKeyConstructor):
    body = BodyKeyBit()


body_cache_key_constructor = BodyCacheKeyConstructor()


class CacheResponse(decorators.CacheResponse):
    def process_cache_response(
        self,
        view_instance,
        view_method,
        request,
        args,
        kwargs,
    ):
        key = self.calculate_key(
            view_instance=view_instance,
            view_method=view_method,
            request=request,
            args=args,
            kwargs=kwargs,
        )

        cache_control = request.headers.get("cache-control", "default").split(",")

        # TODO: accept and handler others directives, such as: no-store, must-revalidate
        if "no-cache" in cache_control:
            valid_cache_control = True
            response_dict = None
        else:
            valid_cache_control = False
            response_dict = self.cache.get(key)

        if not response_dict:
            response = view_method(view_instance, request, *args, **kwargs)
            response = view_instance.finalize_response(request, response, *args, **kwargs)
            response.render()

            if not response.status_code >= 400 or self.cache_errors:
                expiration_date = now() + timedelta(seconds=self.timeout)
                response["Expires"] = handlers.format_date_time(expiration_date.timestamp())
                if valid_cache_control and cache_control:
                    response["Cache-Control"] = f"max-age={self.timeout}"

                response_dict = (
                    response.rendered_content,
                    response.status_code,
                    response.headers.copy(),
                )

                self.cache.set(key, response_dict, self.timeout)
            cache_hit = False
        else:
            try:
                content, status, headers = response_dict
                response = HttpResponse(content=content, status=status)
                response.headers = headers
            except ValueError:
                response = response_dict

            cache_hit = True

        response["X-Cache"] = "HIT" if cache_hit else "MISS"

        if not hasattr(response, "_closable_objects"):
            response._closable_objects = []

        return response


cache_response = CacheResponse
