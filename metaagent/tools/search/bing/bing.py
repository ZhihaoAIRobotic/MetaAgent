# libraries  
import os  
import aiohttp  
import asyncio  
import json  
import logging  


class BingSearchAsync:  
    """  
    Bing Search Retriever (Asynchronous)  
    """  

    def __init__(self, query):  
        """  
        Initializes the BingSearchAsync object  
        Args:  
            query: The search query string  
        """  
        self.query = query  
        self.api_key = self.get_api_key()  
        self.logger = logging.getLogger(__name__)  

    def get_api_key(self):  
        """  
        Gets the Bing API key  
        Returns:  
            The API key as a string  
        """  
        try:  
            api_key = os.environ["BING_API_KEY"]  
        except KeyError:  
            raise Exception(  
                "Bing API key not found. Please set the BING_API_KEY environment variable."  
            )  
        return api_key  

    async def search(self, max_results=7) -> list[dict[str, str]]:  
        """  
        Asynchronously searches the query using Bing API  
        Args:  
            max_results: The maximum number of results to retrieve  
        Returns:  
            A list of search results in dictionary format  
        """  
        print(f"Searching with query {self.query}...")  

        # Bing Search API endpoint  
        url = "https://api.bing.microsoft.com/v7.0/search"  

        headers = {  
            "Ocp-Apim-Subscription-Key": self.api_key,  
            "Content-Type": "application/json",  
        }  
        params = {  
            "responseFilter": "Webpages",  
            "q": self.query,  
            "count": max_results,  
            "setLang": "en-GB",  
            "textDecorations": False,  
            "textFormat": "HTML",  
            "safeSearch": "Strict",  
        }  

        # Perform the asynchronous HTTP request  
        async with aiohttp.ClientSession() as session:  
            try:  
                async with session.get(url, headers=headers, params=params) as resp:  
                    if resp.status != 200:  
                        self.logger.error(  
                            f"Error fetching Bing search results: HTTP {resp.status}"  
                        )  
                        return []  

                    # Parse the response JSON  
                    search_results = await resp.json()  
                    results = search_results.get("webPages", {}).get("value", [])  
            except Exception as e:  
                self.logger.error(  
                    f"Error parsing Bing search results: {e}. Resulting in empty response."  
                )  
                return []  

        # Normalize the results to match the format of the other search APIs  
        search_results = []  
        for result in results:  
            # Skip YouTube results  
            if "youtube.com" in result["url"]:  
                continue  
            search_result = {  
                "title": result["name"],  
                "href": result["url"],  
                "body": result["snippet"],  
            }  
            search_results.append(search_result)  

        return search_results  


# Example usage  
async def main():  
    query = "Python asynchronous programming"  
    bing_search = BingSearchAsync(query)  
    results = await bing_search.search(max_results=5)  
    for result in results:  
        print(result)  


# Run the example  
if __name__ == "__main__":  
    asyncio.run(main())