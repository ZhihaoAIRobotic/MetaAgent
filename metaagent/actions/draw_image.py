#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 17:45
@Author  : alexanderwu
@File    : write_prd.py
"""
from typing import List, Tuple

from metaagent.actions.action import Action, ActionOutput
from metaagent.logs import logger
from metaagent.tools.text2image import TextToImage


class DrawImage(Action):
    def __init__(self, name="", context=None, llm=None):
        super().__init__(name, context, llm)

    def run(self, requirements, *args, **kwargs) -> ActionOutput:
        logger.debug(requirements)
        processor = TextToImage()
        image = processor.process_image(requirements)
        image.save("geeks.jpg")
        # prd = self._aask_v1(prompt, "prd", OUTPUT_MAPPING)
        return "geeks.jpg"
