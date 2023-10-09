import torch
from diffusers import DiffusionPipeline
import cv2
from PIL import Image
import numpy as np
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
from diffusers import UniPCMultistepScheduler


class TextToImageProcessor():
    def __init__(self):
        self.base = DiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, variant="fp16", use_safetensors=True
        )
        self.base.to("cuda")
        self.refiner = DiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-refiner-1.0",
            text_encoder_2=self.base.text_encoder_2,
            vae=self.base.vae,
            torch_dtype=torch.float16,
            use_safetensors=True,
            variant="fp16",
        )
        self.refiner.to("cuda")

    def process_image(self, prompt, n_steps=40, high_noise_frac=0.8):
        image = self.base(
            prompt=prompt,
            num_inference_steps=n_steps,
            denoising_end=high_noise_frac,
            output_type="latent",
        ).images
        image = self.refiner(
            prompt=prompt,
            num_inference_steps=n_steps,
            denoising_start=high_noise_frac,
            image=image,
        ).images[0]
        return image


class TextToImageControlNetProcessor:
    def __init__(self):
        self.text_processor = TextToImageProcessor()
        self.controlnet = ControlNetModel.from_pretrained("lllyasviel/sd-controlnet-canny", torch_dtype=torch.float16)
        self.pipe = StableDiffusionControlNetPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5", controlnet=self.controlnet, torch_dtype=torch.float16
        )
        self.pipe.scheduler = UniPCMultistepScheduler.from_config(self.pipe.scheduler.config)
        self.pipe.enable_model_cpu_offload()

    def process_text_to_image(self, prompts, negative_prompts=None, num_inference_steps=20,seed=2):
        image = self.text_processor.process_image(prompts)
        image = np.array(image)
        low_threshold = 100
        high_threshold = 200
        image = cv2.Canny(image, low_threshold, high_threshold)
        image = image[:, :, None]
        image = np.concatenate([image, image, image], axis=2)
        canny_image = Image.fromarray(image)
        if negative_prompts is None:
            negative_prompts = "monochrome, lowres, bad anatomy, worst quality, low quality"
        generator = torch.manual_seed(seed)
        output = self.pipe(
            prompts,
            canny_image,
            negative_prompt=negative_prompts,
            generator = generator,
            num_inference_steps=num_inference_steps,
        )

        return output.images
if __name__ =="__main__":
    text_to_image_controlnet_processor = TextToImageControlNetProcessor()
    prompts = "Draw a cartoon for me: Subject: Elon Musk, with a white cat next to him. Environment: Grassland under blue sky and white clouds, with rockets in the distance. Behavior: Elon Musk is running freely, and says I am going to publish a new book. Angle: looking up at Elon Musk Composition: wide field of view, Elon Musk takes up a smaller proportion, highlighting the rocket"
    output_images = text_to_image_controlnet_processor.process_text_to_image(prompts,seed=4980)


