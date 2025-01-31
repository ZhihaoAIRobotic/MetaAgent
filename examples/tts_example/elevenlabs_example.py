import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import time

from metaagent.audio.tts_engines import ElevenlabsEngine
from metaagent.audio.text_to_stream import TextToAudioStream

# engine = ElevenlabsEngine()
# stream = TextToAudioStream(engine)
# print("start generation")
# input_text = "start generation"
# time_start = time.time()
# stream.feed(input_text)
# stream.play_async()
# print(stream.first_chunk_generated)
# while not stream.first_chunk_generated:
#     pass
# time_end = time.time()
# print("Time to first token:", time_end - time_start)
import signal
import keyboard

def signal_handler(sig, frame):
    print("\nCtrl+C detected. Cleaning up...")
    stream.stop()
    import sys
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
def dummy_generator():
    yield "This is a longer test with a bit of content."
    # yield "Press spacebar to pause or resume playback. Press Q to quit. "
    # yield "Quick technical note: When you press pause, there may be a brief delay before the audio stops with EdgeEngine. "
    # yield "This happens because the audio player (MPV) pre-buffers some audio data for smooth playback - like water still flowing from a pipe even after you close the tap. "
engine = ElevenlabsEngine()
stream = TextToAudioStream(engine, output_device_index=0)
print("Starting stream - Press SPACE to pause/resume, Q to quit")
stream.feed(dummy_generator()).play_async(log_synthesized_text=True)
is_playing = True
while True:
    if not stream.is_playing():
        print("\nStream finished.")
        break
    if keyboard.is_pressed('space'):
        if is_playing:
            stream.pause()
            print("Paused")
        else:
            stream.resume()
            print("Resumed")
        is_playing = not is_playing
        time.sleep(0.1)  # Debounce
        
    if keyboard.is_pressed('q'):
        print("\nQuitting...")
        break
        
    time.sleep(0.1)

stream.stop()