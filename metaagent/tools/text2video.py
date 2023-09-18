
from diffusers import DiffusionPipeline
import os
from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
from diffusers.utils import export_to_video


class TextTovideoProcessor:
    def __init__(self):
        self.pipeline = DiffusionPipeline.from_pretrained("cerspense/zeroscope_v2_576w")

    def process_text_to_video(self, prompt, output_file_path):
        self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(self.pipeline.scheduler.config)
        self.pipeline.enable_model_cpu_offload()
        video_frames = self.pipeline(prompt, num_inference_steps=25).frames
        video_path = export_to_video(video_frames, output_video_path=output_file_path)



if __name__ == '__main__':
    text2video = TextTovideoProcessor()
    text = 'Elon Musk with his SpaceX.'
    output_file_path = 'output.mp4'
    text2video.process_text_to_video(text, output_file_path)