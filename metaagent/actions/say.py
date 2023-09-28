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
from metaagent.tools.text2audio import TextToSpeech
import torchaudio
from metaagent.minio_bucket import MINIO_OBJ


class Say(Action):
    def __init__(self, name="", context=None, llm=None):
        super().__init__(name, context, llm)
        self.desc = "Speak to the user."

    def run(self, requirements, *args, **kwargs) -> ActionOutput:
        responses = []
        logger.debug(requirements)
        response = self._aask(requirements[-1][-1])
        text2speach = TextToSpeech()
        speech = text2speach.generate_speech(response, 0)
        speech = speech.unsqueeze(0)
        path1 = "speech.wav"
        torchaudio.save(path1, speech, sample_rate=16000)
        MINIO_OBJ.fput_file('metaagent', path1, path1)

        url = MINIO_OBJ.presigned_get_file('metaagent', path1)
        responses.append(url)
        return responses
