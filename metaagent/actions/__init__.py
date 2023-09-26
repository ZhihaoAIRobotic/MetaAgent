# from metaagent.actions.action import Action
# from metaagent.actions.action_output import ActionOutput
from metaagent.actions.say import Say
from metaagent.actions.draw_image import DrawImage
from metaagent.actions.make_videos import MakeVideos
from metaagent.actions.write_script import WriteScript
from metaagent.actions.story_board import StoryBoard


action_dict = {
    'Say': Say,
    'DrawImage': DrawImage,
    'MakeVideos': MakeVideos,
    'WriteScript': WriteScript,
    'StoryBoard': StoryBoard
              }
