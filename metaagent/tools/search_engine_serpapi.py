#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Any, Dict, Optional, Tuple

from pydantic import BaseModel, Field, field_validator
import requests

from metaagent.config import CONFIG


from typing import List

import yagooglesearch


class OutreachSearchResult(BaseModel):
    rank: int
    title: str
    description: str
    url: str


async def get_google_search(query: str, max_search: int = 5):
    client = yagooglesearch.SearchClient(
        query,
        tbs="li:1",
        max_search_result_urls_to_return=max_search,
        http_429_cool_off_time_in_minutes=5,
        http_429_cool_off_factor=1.5,
        # proxy="socks5h://127.0.0.1:9050",
        verbosity=5,
        verbose_output=True,  # False (only URLs) or True (rank, title, description, and URL)
    )
    client.assign_random_user_agent()
    urls = client.search()

    search_response: List[OutreachSearchResult] = []
    for u in urls:
        search_response.append(OutreachSearchResult.model_validate(u))
    return search_response


class SerpAPIWrapper(BaseModel):
    search_engine: Any  #: :meta private:
    params: dict = Field(
        default={
            "engine": "google",
            "google_domain": "google.com",
            "gl": "us",
            "hl": "en",
        }
    )
    serpapi_api_key: Optional[str] = None
    # aiosession: Optional[aiohttp.ClientSession] = None

    class Config:
        arbitrary_types_allowed = True

    @field_validator("serpapi_api_key", mode='before')
    @classmethod
    def check_serpapi_api_key(cls, val: str):
        val = val or CONFIG.serpapi_api_key
        if not val:
            raise ValueError(
                "To use, make sure you provide the serpapi_api_key when constructing an object. Alternatively, "
                "ensure that the environment variable SERPAPI_API_KEY is set with your API key. You can obtain "
                "an API key from https://serpapi.com/."
            )
        return val

    def run(self, query, max_results: int = 8, as_string: bool = True, **kwargs: Any) -> str:
        """Run query through SerpAPI and parse result async."""
        return self._process_response(self.results(query, max_results), as_string=as_string)

    def results(self, query: str, max_results: int) -> dict:
        """Use aiohttp to run query through SerpAPI and return the results async."""

        def construct_url_and_params() -> Tuple[str, Dict[str, str]]:
            params = self.get_params(query)
            params["source"] = "python"
            params["num"] = max_results
            params["output"] = "json"
            url = "https://serpapi.com/search"
            return url, params

        url, params = construct_url_and_params()

        response = requests.get(url, params=params)
        res = response.json()

        return res

    def get_params(self, query: str) -> Dict[str, str]:
        """Get parameters for SerpAPI."""
        _params = {
            "api_key": self.serpapi_api_key,
            "q": query,
        }
        params = {**self.params, **_params}
        return params

    @staticmethod
    def _process_response(res: dict, as_string: bool) -> str:
        """Process response from SerpAPI."""
        # logger.debug(res)
        focus = ["title", "snippet", "link"]
        
        def get_focused(x):
            return {i: j for i, j in x.items() if i in focus}
            
        if "error" in res.keys():
            raise ValueError(f"Got error from SerpAPI: {res['error']}")
        if "answer_box" in res.keys() and "answer" in res["answer_box"].keys():
            toret = res["answer_box"]["answer"]
        elif "answer_box" in res.keys() and "snippet" in res["answer_box"].keys():
            toret = res["answer_box"]["snippet"]
        elif "answer_box" in res.keys() and "snippet_highlighted_words" in res["answer_box"].keys():
            toret = res["answer_box"]["snippet_highlighted_words"][0]
        elif "sports_results" in res.keys() and "game_spotlight" in res["sports_results"].keys():
            toret = res["sports_results"]["game_spotlight"]
        elif "knowledge_graph" in res.keys() and "description" in res["knowledge_graph"].keys():
            toret = res["knowledge_graph"]["description"]
        elif "snippet" in res["organic_results"][0].keys():
            toret = res["organic_results"][0]["snippet"]
        else:
            toret = "No good search result found"

        toret_l = []
        if "answer_box" in res.keys() and "snippet" in res["answer_box"].keys():
            toret_l += [get_focused(res["answer_box"])]
        if res.get("organic_results"):
            toret_l += [get_focused(i) for i in res.get("organic_results")]

        return str(toret) + "\n" + str(toret_l) if as_string else toret_l


if __name__ == "__main__":
    # import fire
    import asyncio
    # fire.Fire(SerpAPIWrapper().run)
    res = asyncio.run(get_google_search("what is the weather in boston"))
    print(res)