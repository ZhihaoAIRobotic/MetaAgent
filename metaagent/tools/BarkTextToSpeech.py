import torch
import scipy.io.wavfile as wavfile
from transformers import BarkModel, AutoProcessor




class BarkTextToSpeech:
    def __init__(self):
        self.model = BarkModel.from_pretrained("suno/bark")
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(self.device)
        self.processor = AutoProcessor.from_pretrained("suno/bark")
    
    def generate_speech(self, text_prompt, voice_preset, output_path):
        inputs = self.processor(text_prompt, voice_preset=voice_preset)
        speech_output = self.model.generate(**inputs.to(self.device))
        sampling_rate = self.model.generation_config.sample_rate
        wavfile.write(output_path, rate=sampling_rate, data=speech_output[0].cpu().numpy())


if __name__ == "__main__":
    bark_tts = BarkTextToSpeech()
    text_prompt = "Let's try generating speech, with Bark, a text-to-speech model"
    voice_preset = "v2/en_speaker_3"
    output_path = "bark_out.wav"
    bark_tts.generate_speech(text_prompt, voice_preset, output_path)

