import json

import requests
import requests_cache
import pandas as pd

from SuperSTATs.utils.constants import ROOT_TBA_URL, TBA_API_KEY


def _cache_non_empty(response):
    # Only cache successful responses with non-empty bodies
    if response is None or not response.ok:
        return False

    body = response.content or b""
    if not body.strip():
        return False

    # For JSON responses, skip common "empty" JSON payloads
    content_type = (response.headers.get("Content-Type") or "").lower()
    if "application/json" in content_type:
        try:
            data = response.json()
            if data in ({}, [], "", None):
                return False
        except (ValueError, json.JSONDecodeError):
            pass

    return True


session = requests_cache.CachedSession(
    cache_name="tba_cache",
    cache_control=True,  # Honor Cache-Control/max-age - handles 304s transparently
    allowable_codes=(200, 304, 404),  # Cache these status codes
    stale_if_error=True,  # Return stale cache on error instead of None
    filter_fn=_cache_non_empty,
)
session.headers["X-TBA-Auth-Key"] = TBA_API_KEY


def get_data(endpoint: str, as_dataframe: bool = False):
    """Fetch data from TBA API with HTTP caching.

    Uses ETag/If-None-Match and Cache-Control headers per TBA API docs:
    https://www.thebluealliance.com/apidocs

    Requests-cache with cache_control=True and stale_if_error=True ensures
    that cached data is returned even when the server returns 304 Not Modified
    or when network errors occur.

    Args:
        endpoint: TBA API endpoint (e.g., "/event/2024arc/teams")
        as_dataframe: If True, return a pandas DataFrame instead of raw JSON

    Returns:
        JSON response as dict/list, pandas DataFrame, or None on error
    """
    endpoint = endpoint.rstrip("/")
    url = f"{ROOT_TBA_URL}{endpoint}"
    try:
        response = session.get(url, timeout=10)

        # With cache_control=True, requests-cache handles 304s transparently
        # by returning cached data. We only process 200 status codes here.
        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            return None

        data = response.json()
        return pd.DataFrame().from_dict(data) if as_dataframe and data else data

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
