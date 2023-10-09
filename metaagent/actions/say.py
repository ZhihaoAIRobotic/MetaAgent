from typing import List
from metaagent.logs import logger
from metaagent.tools.text2audio import TextToSpeech
import torchaudio
from metaagent.LLMs.openai_llm import OpenAIGPTAPI
from metaagent.minio_bucket import MINIO_OBJ
from metaagent.actions.action import Action


class Say(Action):
    def __init__(self, llm=None):
        super().__init__()
        self.llm = llm
        if self.llm is None:
            self.llm = OpenAIGPTAPI()
        self.desc = "Speak to the user."

    def run(self, requirements, *args, **kwargs) -> List:
        responses = []
        logger.debug(requirements)
        response = self.llm.aask(requirements[-1][-1])
        text2speach = TextToSpeech()
        speech = text2speach.generate_speech(response, 0)
        speech = speech.unsqueeze(0)
        path1 = "speech.wav"
        torchaudio.save(path1, speech, sample_rate=16000)
        MINIO_OBJ.fput_file('metaagent', path1, path1)

        url = MINIO_OBJ.presigned_get_file('metaagent', path1)
        responses.append(url)
        print(url)
        return responses
