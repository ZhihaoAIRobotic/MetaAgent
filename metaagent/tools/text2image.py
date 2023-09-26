import torch
from diffusers import DiffusionPipeline
from PIL import Image 


# lpw_stable_diffusion
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
    
# pipe = DiffusionPipeline.from_pretrained(
#     "hakurei/waifu-diffusion", custom_pipeline="lpw_stable_diffusion", torch_dtype=torch.float16, use_safetensors=True
# )
# pipe = pipe.to("cuda")

# prompt = "best_quality (1girl:1.3) bow bride brown_hair closed_mouth frilled_bow frilled_hair_tubes frills (full_body:1.3) fox_ear hair_bow hair_tubes happy hood japanese_clothes kimono long_sleeves red_bow smile solo tabi uchikake white_kimono wide_sleeves cherry_blossoms"
# neg_prompt = "lowres, bad_anatomy, error_body, error_hair, error_arm, error_hands, bad_hands, error_fingers, bad_fingers, missing_fingers, error_legs, bad_legs, multiple_legs, missing_legs, error_lighting, error_shadow, error_reflection, text, error, extra_digit, fewer_digits, cropped, worst_quality, low_quality, normal_quality, jpeg_artifacts, signature, watermark, username, blurry"

# pipe.text2img(prompt, negative_prompt=neg_prompt, width=512, height=512, max_embeddings_multiples=3).images[0]