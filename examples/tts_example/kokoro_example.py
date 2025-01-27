import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from metaagent.audio.engines import KokoroEngine
from metaagent.audio.text_to_stream import TextToAudioStream

def dummy_generator():
    yield "This is the first voice model speaking. "
    yield "The elegance of the style and its flow is simply captivating. "
    yield "We’ll soon switch to another voice model. "
def dummy_generator_2():
    yield "And here we are! "
    yield "You’re now listening to the second voice model, with a different style and tone. "
# Adjust these paths to your local setup
kokoro_root = "/home/lzh/CodeNew/MetaAgenttest/Kokoro-82M"
# Initialize the engine with the first voice
engine = KokoroEngine(
    kokoro_root=kokoro_root,
)
# Create a TextToAudioStream with the engine
stream = TextToAudioStream(engine)
# Play with the first model
print("Playing with the first model...")
stream.feed(dummy_generator())
stream.play(log_synthesized_text=True)

# Pick one of: 
# "af_nicole", 
# "af",
# "af_bella",
# "af_sarah",
# "am_adam",
# "am_michael",
# "bf_emma",
# "bf_isabella",
# "bm_george",
# "bm_lewis",
# "af_sky"  
engine.set_voice("af_sky")
stream.feed(dummy_generator_2())
stream.play(log_synthesized_text=True)

# Shutdown the engine
engine.shutdown()