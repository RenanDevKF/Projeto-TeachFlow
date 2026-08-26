from django.utils.cache import add_never_cache_headers


class AuthenticatedNoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        content_type = response.get('Content-Type', '')

        if (
            request.user.is_authenticated
            and content_type.startswith('text/html')
        ):
            add_never_cache_headers(response)

        return response