from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

def pdf2markdown(filepath: str):
    converter = PdfConverter(
        artifact_dict=create_model_dict(),
    )
    rendered = converter(filepath)
    text, _, images = text_from_rendered(rendered)
    return text, images


if __name__ == "__main__":
    import time
    start = time.time()
    text, images = pdf2markdown("example.pdf")
    end = time.time()
    print(f"Time taken: {end - start} seconds")
    # print(text)
    # save text to a file
    with open("text.md", "w") as f:
        f.write(text)
    print(images)
    # show images images is a dict
    for key, image in images.items():
        image.show()
        # after press enter, continue to the next image
        input()
