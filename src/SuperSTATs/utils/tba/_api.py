import requests
import requests_cache
import pandas as pd
import streamlit as st

current_year = pd.Timestamp.now().year
root_url = "https://www.thebluealliance.com/api/v3"
api_key = st.secrets["TBA_API"]

# Create cached session with TBA API best practices
# - Respects ETag/If-None-Match headers for 304 responses
# - Honors Cache-Control/max-age from TBA
# - In-memory cache (no file persistence)
# - With cache_control=True, 304 responses are handled transparently
session = requests_cache.CachedSession(
    cache_name="tba_cache",
    backend="memory",
    expire_after=None,  # Respect Cache-Control headers from TBA
    cache_control=True,  # Honor Cache-Control/max-age - handles 304s transparently
    allowable_codes=(200, 304, 404),  # Cache these status codes
    stale_if_error=True,  # Return stale cache on error instead of None
)
session.headers["X-TBA-Auth-Key"] = api_key


def get_data(endpoint, as_dataframe=False):
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
    url = f"{root_url}{endpoint}"
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
