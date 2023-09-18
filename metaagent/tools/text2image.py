import torch
from diffusers import DiffusionPipeline
from PIL import Image 


class TextToImage():
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
    

if __name__ == '__main__':
    text = 'Elon Musk is the CEO of Tesla.'
    processor = TextToImage()
    image = processor.process_image(text)
    print(type(image))
    image.save("geeks.jpg")
    
