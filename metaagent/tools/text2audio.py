import torch
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
import torchaudio
from torchaudio.utils import download_asset
from docarray.typing import AudioBytes, AudioTensor


class TextToSpeechProcessor:
    def __init__(self):
        self.processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
        self.model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
        self.vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

    def generate_speech(self, text, ids):
        inputs = self.processor(text=text, return_tensors="pt")
        embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
        speaker_embeddings = torch.tensor(embeddings_dataset[ids]["xvector"]).unsqueeze(0)
        speech = self.model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=self.vocoder)
        return speech


if __name__ == '__main__':
    text2speach = TextToSpeechProcessor()
    text = 'Elon Musk is the CEO of Tesla.'
    ids = 0
    speech = text2speach.generate_speech(text, ids)
    print(type(speech))
    path1 = "speech.wav"
    SAMPLE_WAV = download_asset("tutorial-assets/Lab41-SRI-VOiCES-src-sp0307-ch127535-sg0042.wav")
    waveform, sample_rate = torchaudio.load(SAMPLE_WAV)
    print(waveform)
    # add one more dimension to fit the shape of speech
    speech = speech.unsqueeze(0)
    print(speech)
    torchaudio.save(path1, speech, sample_rate=16000)

