#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 17:45
@Author  : alexanderwu
@File    : write_prd.py
"""
from typing import List, Tuple

from metaagent.actions.action import Action, ActionOutput
from metaagent.actions.search_and_summarize import SearchAndSummarize, SEARCH_AND_SUMMARIZE_SYSTEM_EN_US
from metaagent.logs import logger


class DrawImage(Action):
    def __init__(self, name="", context=None, llm=None):
        super().__init__(name, context, llm)

    def run(self, requirements, *args, **kwargs) -> ActionOutput:
        print('Draw image######################################')
        logger.debug(requirements)
        # prd = self._aask_v1(prompt, "prd", OUTPUT_MAPPING)
        return 0
