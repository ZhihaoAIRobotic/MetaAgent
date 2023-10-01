



import os

class FaceSwapper:
    def __init__(self, device="cuda", processor="face_swapper face_enhancer", video_encoder="libx264",
                 video_quality="35", temp_format="jpg", temp_quality="0", keep_fps=True, skip_audio=False,
                 keep_frames=False, many_faces=False,position='1',similar_face_distance='1005'):
        self.device = device
        self.processor = processor
        self.video_encoder = video_encoder
        self.video_quality = video_quality
        self.temp_format = temp_format
        self.temp_quality = temp_quality
        self.keep_fps = keep_fps
        self.skip_audio = skip_audio
        self.keep_frames = keep_frames
        self.many_faces = many_faces
        self.reference_face_position = position
        self.similar_face_distance = similar_face_distance

    def swap_faces(self, source, target, output):
        keep_fps = "--keep-fps" if self.keep_fps else ""
        skip_audio = "--skip-audio" if self.skip_audio else ""
        keep_frames = "--keep-frames" if self.keep_frames else ""
        many_faces = "--many-faces" if self.many_faces else ""

        cmd = f"swapper.py --execution-provider {self.device} -s {source} -t {target} -o {output} --similar-face-distance {self.similar_face_distance} --frame-processor {self.processor} --reference-face-position {self.reference_face_position} --output-video-encoder {self.video_encoder} --output-video-quality {self.video_quality} {keep_fps} {skip_audio} {keep_frames} {many_faces} --temp-frame-format {self.temp_format} --temp-frame-quality {self.temp_quality}"
        print("cmd: " + cmd)

        # Download models if not already downloaded
        self.download_models()

        # Run the command
        os.system(f"python {cmd}")

    @staticmethod
    def download_models():
        # Create 'models' directory if not already present
        if not os.path.exists("models"):
            print('model not exists')

            os.makedirs("models")
        else:
          print('model exists')
        # Download face swapper model
        swapper_model_path = "models/inswapper_128.onnx"
        if not os.path.exists(swapper_model_path):
            print('swapper model not exists')
            os.system("wget https://github.com/dream80/roop_colab/releases/download/v0.0.1/inswapper_128.onnx -O " + swapper_model_path)
        else:
          print('swapper model exists')

        # Download face enhancer model
        enhancer_model_path = "models/GFPGANv1.4.pth"
        if not os.path.exists(enhancer_model_path):
            os.system("wget https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth -O " + enhancer_model_path)            


if __name__ == '__main__':
    source = "./example/yuner.jpeg"
    target = "./example/yaya.mp4"
    output = "./example/yaya_out.mp4"
    
    swapper = FaceSwapper(processor = 'face_swapper',many_faces=True)
    swapper.swap_faces(source=source, target=target, output=output)
