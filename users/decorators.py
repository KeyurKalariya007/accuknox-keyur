from django.core.cache import cache
from functools import wraps
from django.http import HttpResponseForbidden

def rate_limit(key, rate, method='GET'):
    """
    Custom rate limiting decorator.

    :param key: Unique key for rate limiting (e.g., user id or IP address).
    :param rate: Maximum number of requests allowed per minute.
    :param method: HTTP method to limit (default is 'GET').
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            user_id = request.user.id if request.user.is_authenticated else 'anonymous'
            cache_key = f"rate_limit:{key}:{user_id}:{method}"
            count = cache.get(cache_key, 0)
            if count >= rate:
                return HttpResponseForbidden("Rate limit exceeded.")
            cache.set(cache_key, count + 1, 60)  # Increase count and set expiry to 60 seconds
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator
