#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/6 20:15
@Author  : alexanderwu
@File    : search_engine.py
"""

import importlib
from typing import Callable, Coroutine, Literal, overload, List, Dict

from metaagent.config import CONFIG
# from metaagent.tools import SearchEngineType
from enum import Enum

class SearchEngineType(Enum):
    SERPAPI_GOOGLE = "serpapi"
    SERPER_GOOGLE = "serper"
    DIRECT_GOOGLE = "google"
    DUCK_DUCK_GO = "ddg"
    CUSTOM_ENGINE = "custom"

class SearchEngine:
    """Class representing a search engine.

    Args:
        engine: The search engine type. Defaults to the search engine specified in the config.
        run_func: The function to run the search. Defaults to None.

    Attributes:
        run_func: The function to run the search.
        engine: The search engine type.
    """
    def __init__(
        self,
        engine: SearchEngineType = None, run_func=None
    ):
        engine = SearchEngineType.SERPAPI_GOOGLE
        module = "metaagent.tools.search_engine_serpapi"
        run_func = importlib.import_module(module).SerpAPIWrapper().run

        self.engine = engine
        self.run_func = run_func

    @overload
    def run(
        self,
        query: str,
        max_results: int = 8,
        as_string: Literal[True] = True,
    ) -> str:
        ...

    @overload
    def run(
        self,
        query: str,
        max_results: int = 8,
        as_string: Literal[False] = False,
    ) -> List[Dict[str, str]]:
        ...

    def run(self, query: str, max_results: int = 8, as_string: bool = True):
        """Run a search query.

        Args:
            query: The search query.
            max_results: The maximum number of results to return. Defaults to 8.
            as_string: Whether to return the results as a string or a list of dictionaries. Defaults to True.

        Returns:
            The search results as a string or a list of dictionaries.
        """
        return self.run_func(query, max_results=max_results, as_string=as_string)
