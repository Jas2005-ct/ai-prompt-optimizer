"""Shared utility functions."""
import hashlib
import json
from django.core.cache import cache


def generate_cache_key(prefix: str, data: dict) -> str:
    """Generate a deterministic cache key from a prefix and data dict."""
    data_str = json.dumps(data, sort_keys=True)
    hash_val = hashlib.md5(data_str.encode()).hexdigest()
    return f"{prefix}:{hash_val}"


def get_or_set_cache(key: str, compute_fn, timeout: int = 300):
    """Generic cache get-or-set helper."""
    result = cache.get(key)
    if result is None:
        result = compute_fn()
        cache.set(key, result, timeout)
    return result


def build_api_response(success: bool, data=None, message: str = '', status_code: int = 200) -> dict:
    """Standardized API response builder."""
    return {
        'success': success,
        'message': message,
        'data': data,
        'status_code': status_code,
    }
