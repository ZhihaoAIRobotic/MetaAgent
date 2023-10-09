from metaagent.tools.text2image import TextToImage
from metaagent.minio_bucket import MINIO_OBJ
from metaagent.actions.action import Action


class DrawImage(Action):
    def __init__(self):
        super().__init__()
        self.desc = "Draw images. If the user need a image, then use this action."
        self.processor = TextToImage()

    def run(self, requirements, *args, **kwargs):
        # logger.debug(requirements)
        responses = []
        number = 0
        for i in requirements[-1]:
            print('$$$$$$$$$$$$$$$InputForImage$$$$$$$$$$$$$$$$')
            print(i)
            number += 1
            image = self.processor.process_image(i)
            image.save("geeks.jpg")
            print(f"geeks{number}.jpg")
            MINIO_OBJ.fput_file('cartoonist', f"geeks{number}.jpg", "geeks.jpg")
            url = MINIO_OBJ.presigned_get_file('cartoonist', f"geeks{number}.jpg")
            print(url)
            responses.append(url)
        return responses
