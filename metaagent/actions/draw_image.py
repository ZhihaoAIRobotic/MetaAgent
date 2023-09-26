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
        self.desc = "Draw image for the user."
        self.processor = TextToImage()

    def run(self, requirements, *args, **kwargs) -> ActionOutput:
        # logger.debug(requirements)
        responses = []
        number = 0
        for i in requirements[-1]:
            print('$$$$$$$$$$$$$$$InputForImage$$$$$$$$$$$$$$$$')
            print(i)
            number += 1
            image = self.processor.process_image(i)
            image.save("geeks.jpg")
            print(f"geeks{number}.jpg")
            MINIO_OBJ.fput_file('cartoonist', f"geeks{number}.jpg", "geeks.jpg")
            url = MINIO_OBJ.presigned_get_file('cartoonist', f"geeks{number}.jpg")
            print(url)
            responses.append(url)
        return responses
