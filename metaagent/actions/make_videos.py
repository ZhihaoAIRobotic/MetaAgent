from metaagent.tools.text2video import TextToVideo
from metaagent.minio_bucket import MINIO_OBJ
from metaagent.actions.action import Action


class MakeVideos(Action):
    def __init__(self):
        super().__init__()
        self.desc = "Make videos. If the user need a video, then use this action."

    def run(self, requirements, *args, **kwargs):
        responses = []
        processor = TextToVideo()
        output_file_path = 'output.mp4'
        processor.process_text_to_video(requirements[-1][-1], output_file_path)
        MINIO_OBJ.fput_file('metaagent', output_file_path, output_file_path)
        url = MINIO_OBJ.presigned_get_file('metaagent', output_file_path)
        responses.append(url)
        return responses
