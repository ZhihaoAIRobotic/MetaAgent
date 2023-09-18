# from metaagent.actions.action import Action
# from metaagent.actions.action_output import ActionOutput
from metaagent.actions.write_prd import WritePRD
from metaagent.actions.text2audio import GenerateAudio
from metaagent.actions.text2image import DrawImage

action_dict = {
    'WritePRD': WritePRD,
    'GenerateAudio': GenerateAudio,
    'DrawImage': DrawImage
              }
