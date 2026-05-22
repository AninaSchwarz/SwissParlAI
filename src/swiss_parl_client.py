import requests
import time
import logging
import re
from typing import Dict, Any, Iterator, Optional


def strip_html(text):
    return re.sub(r"<[^>]+>", " ", text).strip()


class SwissParlClient:
    """
    Client for interacting with the Swiss Parliament OData API.

    This class provides functionality to fetch data from the Swiss Parliament's OData
    API endpoint. It supports automatic pagination for fetching large datasets and
    includes retry logic for handling transient network errors.

    :ivar timeout: Timeout duration (in seconds) for API calls.
    :type timeout: int
    :ivar session: HTTP session used for making API requests with custom headers.
    :type session: requests.Session
    """
    BASE_URL = "https://ws.parlament.ch/OData.svc"

    def __init__(self, user_agent: str = "UniBernResearch/1.0", timeout: int = 30):
        """
        Initializes the HTTP client with default or provided user agent and timeout settings.

        The client sets up an HTTP session with headers configured to include a user agent
        string and accept JSON responses. It also allows a timeout value to be specified
        to determine the maximum time waiting for a server's response.

        :param user_agent: The User-Agent string to be included in the HTTP headers.
            Default is "UniBernResearch/1.0".
        :param timeout: The timeout value, in seconds, for the HTTP requests.
            Default is 30 seconds.
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept": "application/json"
        })

    def fetch_stream(self, entity: str, params: Dict[str, Any] = None) -> Iterator[Dict[str, Any]]:
        """
        Fetches and yields a stream of data records from the OData service endpoint corresponding to the specified
        entity. This method handles pagination automatically using the '__next' link in the OData response. Data
        is fetched in JSON format.

        :param entity: The name of the entity to fetch data from.
        :type entity: str
        :param params: Additional query parameters to include in the request. If not provided, a default JSON
            format parameter is used.
        :type params: Dict[str, Any], optional
        :return: An iterator over dictionaries, each representing a data record from the OData service.
        :rtype: Iterator[Dict[str, Any]]
        """
        url = f"{self.BASE_URL}/{entity}"
        current_params = params.copy() if params else {"$format": "json"}
        # Ensure we always ask for JSON
        current_params["$format"] = "json"

        while url:
            data = self._fetch_with_retry(url, current_params)

            if not data:
                break

            # Handle generic OData response wrapper 'd'
            d_block = data.get('d', {})
            # Handle results list or single object
            results = d_block.get('results', []) if isinstance(d_block, dict) else d_block

            # Yield data to the caller immediately
            yield from results

            # Handle Pagination (The "Next" Link)
            if isinstance(d_block, dict) and '__next' in d_block:
                url = d_block['__next']
                # The __next link usually contains the params, so we reset ours
                current_params = {"$format": "json"}
            else:
                url = None

    def fetch_single(self, entity: str, params: Dict[str, Any] = None) -> Optional[Dict]:
        """
        Fetches a single entity from the server by making a request to the specified
        endpoint. The request will append default JSON format parameters, ensuring
        a predictable data format in the response.

        :param entity: The name of the entity to fetch from the server.
        :type entity: str
        :param params: Additional query parameters to include in the request. If not
            provided, a default parameter "$format" set to "json" will be used.
        :type params: Dict[str, Any], optional
        :return: A dictionary containing the fetched entity data, or None if no
            data is returned or the response is empty.
        :rtype: Optional[Dict]
        """
        url = f"{self.BASE_URL}/{entity}"
        params = params or {"$format": "json"}
        params["$format"] = "json"

        data = self._fetch_with_retry(url, params)
        if not data: return None

        d_block = data.get('d', {})
        # If it returns a list of 1 item, unwrap it
        if isinstance(d_block, list) and len(d_block) > 0:
            return d_block[0]
        return d_block

    def _fetch_with_retry(self, url: str, params: Dict) -> Optional[Dict]:
        """
        Retries fetching content from a given URL using an HTTP GET request and applies exponential backoff
        in case of network-related errors. Stops retrying if the response status is either 400 (Bad Request)
        or after exceeding the maximum retry limit. Returns the JSON response on success.

        :param url: The URL from which data needs to be fetched
        :type url: str
        :param params: A dictionary of query parameters to include in the GET request
        :type params: Dict
        :return: A JSON-parsed dictionary response if the request is successful, None if the response
                 status is 404 or 400, or if all retries fail
        :rtype: Optional[Dict]
        """
        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)

                # 404 is valid (Data not found), not a crash
                if response.status_code == 404:
                    return None

                # 400 is valid (Bad Request - e.g., invalid filter), stop retrying
                if response.status_code == 400:
                    logging.error(f"❌ API 400 Bad Request: {url}")
                    return None

                response.raise_for_status()
                return response.json()

            except requests.RequestException as e:
                logging.warning(f"⚠️ Network error {url} (Attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(2 ** attempt)  # Exponential backoff (1s, 2s, 4s)

        logging.error(f"❌ Failed to fetch {url} after {max_retries} attempts.")
        return None

if __name__ == "__main__":

    client = SwissParlClient()
    params = {"$filter": "Language eq 'DE'", "$top": 3}

    for record in client.fetch_stream("Transcript", params):
        raw_date = record.get("MeetingDate") or ""
        date     = raw_date[:10] if "T" in raw_date else f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
        speaker  = record.get("SpeakerFullName") or "Unknown speaker"
        preview  = strip_html(record.get("Text") or "")[:120]
        print(f"{date} | {speaker}")
        print(f"  {preview}...")
        print()