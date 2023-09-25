from metaagent.tools.text2video import TextToVideo
from metaagent.actions.action import Action, ActionOutput
from metaagent.minio_bucket import MINIO_OBJ


class MakeVideos(Action):
    def __init__(self, name="", context=None, llm=None):
        super().__init__(name, context, llm)
        self.desc = "Make videos for the user."

    def run(self, requirements, *args, **kwargs) -> ActionOutput:
        processor = TextToVideo()
        output_file_path = 'output.mp4'
        processor.process_text_to_video(requirements[-1], output_file_path)
        MINIO_OBJ.fput_file('metaagent', output_file_path, output_file_path)
        url = MINIO_OBJ.presigned_get_file('metaagent', output_file_path)
        return url
