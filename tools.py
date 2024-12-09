from fastapi import FastAPI
from typing import List, Dict, Union , Optional
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from typing import List, Dict, Union , Optional
import requests
import json
from pydantic import BaseModel, Field
from typing import List, Dict, Union, Optional
from fastapi.middleware.cors import CORSMiddleware
from models import *
load_dotenv()

def fetch_stable_coins(top_m: int) -> List[Dict[str, Union[str, float]]]:
    """
    Fetches stablecoins data from the API and filters the top `top_m` stablecoins.

    Args:
        top_m (int): The number of top stablecoins to retrieve.

    Returns:
        List[Dict[str, Union[str, float]]]: A list of dictionaries with stablecoin details or an error message.
    """
    url = "https://stablecoins.llama.fi/stablecoins?includePrices=true"
    
    try:
        # Perform the GET request with a timeout
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses

        try:
            # Parse JSON response
            stablecoins_data = response.json()
            stablecoins = stablecoins_data.get("peggedAssets", [])
            
            # Validate that stablecoins is a list
            if not isinstance(stablecoins, list):
                raise ValueError("Unexpected format: 'peggedAssets' should be a list.")

            # Filter and process the top `top_m` stablecoins
            stablecoins = stablecoins[:top_m]
            filtered_stablecoins = [
                {
                    "Name": coin.get("name", "Unknown"),
                    "Symbol": coin.get("symbol", "Unknown"),
                    "Price": coin.get("price", 0.0),
                    "GecKoId": coin.get("gecko_id", "Unknown")
                }
                for coin in stablecoins
            ]

            return filtered_stablecoins

        except (ValueError, KeyError) as e:
            raise RuntimeError(f"Error processing the API response: {e}")

    except requests.exceptions.Timeout:
        raise RuntimeError("The request timed out. Please try again later.")
    except requests.exceptions.HTTPError as http_err:
        raise RuntimeError(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        raise RuntimeError(f"Request failed: {req_err}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")


# Define the input schema for internet search


# Define the internet_search function
def internet_search(query: str, region: Optional[str] = "wt-wt", max_results: Optional[int] = 5) -> InternetSearchOutput:
    """
    Performs an internet search using DuckDuckGo Search (DDGS).
    
    Args:
        query (str): The search query.
        region (Optional[str]): The region for the search, default is "wt-wt".
        max_results (Optional[int]): The maximum number of results to retrieve, default is 5.

    Returns:
        InternetSearchOutput: An object containing the search results.

    Raises:
        ValueError: If the query is empty or None.
        RuntimeError: If there is an error during the search process.
    """
    if not query:
        raise ValueError("Search query cannot be empty or None.")
    
    params = {
        "keywords": query,
        "region": region,
        "max_results": max_results,
    }

    try:
        with DDGS() as ddg:
            results = ddg.text(**params)
            return InternetSearchOutput(results=list(results))
    except ValueError as ve:
        raise ValueError(f"Invalid parameter provided: {ve}")
    except ConnectionError as ce:
        raise RuntimeError(f"Network issue occurred while performing the search: {ce}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred during the internet search: {e}")

# Define the input and output schemas for the new GetPools tool

# Define the function to fetch top liquidity pools by TVL
def get_and_display_top_pools_by_tvl(top_n: int = 5) -> GetPoolsOutput:
    """
    Fetches and displays the top pools by TVL (Total Value Locked) from a specified API.

    Args:
        top_n (int): The number of top pools to retrieve. Default is 5.

    Returns:
        GetPoolsOutput: An object containing the top pools or an error message.

    Raises:
        RuntimeError: If an unexpected error occurs during the process.
    """
    url = "https://yields.llama.fi/pools"
    headers = {"accept": "application/json"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad status codes

        pools_data = response.json()
        pools = pools_data.get("data", [])
        
        # Ensure the data is in the expected format
        if not isinstance(pools, list):
            raise ValueError("Unexpected format: 'data' is not a list.")
        
        # Sort and filter the top pools
        sorted_pools = sorted(pools, key=lambda x: x.get("tvlUsd", 0), reverse=True)[:top_n]
        top_pools = [
            {
                "Project": pool.get('project', 'Unknown'),
                "Symbol": pool.get('symbol', 'Unknown'),
                "TVL (USD)": pool.get('tvlUsd', 0),
                "APY": pool.get('apy', 'N/A'),
                "Chain": pool.get('chain', 'Unknown')
            } for pool in sorted_pools
        ]
        return GetPoolsOutput(pools=top_pools)

    except requests.exceptions.Timeout:
        raise RuntimeError("The request timed out. Please try again later.")
    except requests.exceptions.HTTPError as http_err:
        raise RuntimeError(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        raise RuntimeError(f"An error occurred while making the request: {req_err}")
    except ValueError as ve:
        raise RuntimeError(f"Data format error: {ve}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")

    


# Function without using an output Pydantic model
def get_stable_coins(top_m: int) -> List[Dict[str, Union[str, float]]]:
    """
    Fetches stablecoins data from the API and filters the top `top_m` stablecoins.

    Args:
        top_m (int): Number of top stablecoins to retrieve.

    Returns:
        List[Dict[str, Union[str, float]]]: A list of dictionaries with stablecoin details or an error message.
    """
    url = "https://stablecoins.llama.fi/stablecoins?includePrices=true"

    try:
        # Perform the GET request with a timeout
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        try:
            # Parse JSON response
            stablecoins_data = response.json()
            stablecoins = stablecoins_data.get("peggedAssets", [])

            # Validate that stablecoins is a list
            if not isinstance(stablecoins, list):
                raise ValueError("Unexpected data format: 'peggedAssets' is not a list.")

            # Filter and process the top `top_m` stablecoins
            stablecoins = stablecoins[:top_m]
            filtered_stablecoins = [
                {
                    "Name": coin.get("name", "Unknown"),
                    "Symbol": coin.get("symbol", "Unknown"),
                    "Price": coin.get("price", 0.0),
                    "GeckoId": coin.get("gecko_id", "Unknown")
                }
                for coin in stablecoins
            ]

            return filtered_stablecoins

        except (ValueError, KeyError) as e:
            raise RuntimeError(f"Error processing the API response: {e}")

    except requests.exceptions.Timeout:
        raise RuntimeError("The request timed out. Please try again later.")
    except requests.exceptions.HTTPError as http_err:
        raise RuntimeError(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        raise RuntimeError(f"Request failed: {req_err}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")

    



def get_stable_coin_prices(dummy):
    """
    Fetches stablecoin prices from the API.

    Args:
        dummy: Placeholder argument for compatibility.

    Returns:
        dict: Stablecoin prices or an error message.
    """
    url = "https://stablecoins.llama.fi/stablecoinprices"
    try:
        # Perform the GET request with a timeout
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        try:
            # Parse JSON response
            stablecoin_prices = response.json()
            if not isinstance(stablecoin_prices, list) or not stablecoin_prices:
                raise ValueError("Unexpected JSON format: Expected a non-empty list.")
            return stablecoin_prices[0]
        except ValueError as ve:
            raise RuntimeError(f"Error parsing JSON response: {ve}")
        except IndexError:
            raise RuntimeError("The JSON response is empty or does not contain expected data.")

    except requests.exceptions.Timeout:
        raise RuntimeError("The request timed out. Please try again later.")
    except requests.exceptions.HTTPError as http_err:
        raise RuntimeError(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        raise RuntimeError(f"Request failed: {req_err}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")
