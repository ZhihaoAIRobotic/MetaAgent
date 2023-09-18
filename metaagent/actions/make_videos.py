from metaagent.tools.text2video import TextToVideo
from metaagent.actions.action import Action, ActionOutput


class MakeVideos(Action):
    def __init__(self, name="", context=None, llm=None):
        super().__init__(name, context, llm)

    def run(self, requirements, *args, **kwargs) -> ActionOutput:
        processor = TextToVideo()
        output_file_path = 'output.mp4'
        processor.process_text_to_video(requirements, output_file_path)
        return output_file_path
