import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import time

from metaagent.audio.tts_engines.parler_engine import ParlerEngine
from metaagent.audio.text_to_stream import TextToAudioStream

engine = ParlerEngine()
stream = TextToAudioStream(engine)
print("start generation")
while True:
    input_text = input()
    time_start = time.time()
    stream.feed(input_text)
    stream.play_async()
    print(stream.first_chunk_generated)
    while not stream.first_chunk_generated:
        pass
    time_end = time.time()
    print("Time to first token:", time_end - time_start)