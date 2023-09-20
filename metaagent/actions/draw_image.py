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
from metaagent.minio_bucket import MINIO_OBJ


class DrawImage(Action):
    def __init__(self, name="", context=None, llm=None):
        super().__init__(name, context, llm)

    def run(self, requirements, *args, **kwargs) -> ActionOutput:
        logger.debug(requirements)
        processor = TextToImage()
        image = processor.process_image(requirements[-1])
        image.save("geeks.jpg")
        MINIO_OBJ.fput_file('metaagent', "geeks.jpg", "geeks.jpg")
        url = MINIO_OBJ.presigned_get_file('metaagent', "geeks.jpg")
        return url
