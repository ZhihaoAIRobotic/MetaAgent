# from metaagent.actions.action import Action
# from metaagent.actions.action_output import ActionOutput
from metaagent.actions.write_prd import WritePRD
from metaagent.actions.say import Say
from metaagent.actions.draw_image import DrawImage
from metaagent.actions.make_videos import MakeVideos

action_dict = {
    'WritePRD': WritePRD,
    'Say': Say,
    'DrawImage': DrawImage,
    'MakeVideos': MakeVideos
              }
