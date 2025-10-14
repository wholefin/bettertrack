import os
import time
from datetime import datetime, timedelta
from pathlib import Path
import requests


# Load .env file if it exists (for development/testing)
try:
    from dotenv import load_dotenv

    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed, rely on environment variables

# In-memory cache for prices (ticker -> (price, timestamp))
_PRICE_CACHE = {}
_CACHE_DURATION = timedelta(hours=1)  # Cache prices for 1 hour


def get_current_price(ticker: str) -> float:
    """
    Get the current price for a ticker using Alpha Vantage API.

    This function uses Alpha Vantage's GLOBAL_QUOTE endpoint which provides
    real-time price data. Prices are cached for 1 hour to avoid hitting API limits.

    Parameters
    ----------
    ticker : str
        The ticker symbol to fetch the price for.

    Returns
    -------
    float
        The current price of the ticker.

    Raises
    ------
    ValueError
        If no price data is found or API key is missing.
    RuntimeError
        If the API request fails.

    Notes
    -----
    Requires ALPHAVANTAGE_API_KEY environment variable to be set.
    Free tier allows 25 requests/day and 5 requests/minute.
    """
    # Check cache first
    if ticker in _PRICE_CACHE:
        cached_price, cached_time = _PRICE_CACHE[ticker]
        if datetime.now() - cached_time < _CACHE_DURATION:
            return cached_price

    # Get API key from environment
    api_key = os.environ.get("ALPHAVANTAGE_API_KEY")
    if not api_key:
        raise ValueError(
            "ALPHAVANTAGE_API_KEY environment variable not set. "
            "Get a free key at https://www.alphavantage.co/support/#api-key"
        )

    # Make API request
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": ticker,
        "apikey": api_key,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Check for API errors
        if "Error Message" in data:
            raise ValueError(f"Invalid ticker symbol: {ticker}")

        if "Note" in data:
            # API rate limit message
            raise RuntimeError(f"Alpha Vantage API rate limit reached. {data['Note']}")

        # Extract price from response
        quote = data.get("Global Quote", {})
        if not quote:
            raise ValueError(f"No price data found for ticker: {ticker}")

        price_str = quote.get("05. price")
        if not price_str:
            raise ValueError(f"No price field in response for ticker: {ticker}")

        price = float(price_str)

        # Cache the result
        _PRICE_CACHE[ticker] = (price, datetime.now())

        # Small delay to respect rate limits (5 calls/minute = 12 seconds between calls)
        time.sleep(0.5)

        return price

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch price for {ticker}: {e}")


def clear_price_cache():
    """Clear the in-memory price cache."""
    global _PRICE_CACHE
    _PRICE_CACHE = {}
