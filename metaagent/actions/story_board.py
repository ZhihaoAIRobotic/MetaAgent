from metaagent.models.openai_llm import OpenAIGPTAPI
from metaagent.actions.action import Action


PREFIX_SETTINGS = """
Based on the script, you need to be a very good text storyboard writer to create comics.
I want you to storyboard the content of the script and infer the scene based on the original text description after storyboarding;
1. It is necessary to infer and supplement missing or hidden information, including clothing, hairstyle, hair color, character emotion, character body movements, style description (including but not limited to Age description, space description, time period description, geographical environment description, weather description), item description (including but not limited to animals, plants, food, fruits, toys), picture perspective (including but not limited to character proportions, Lens depth description, observation angle description).
2. Through lens language description, richer character emotions and emotional states can be portrayed. Once understood, new descriptions can be generated through sentences.
Please note that the different storyboards need to be seprated by "==="
"""

OUTPUT_DESCRIPTION = """
The output text storyboard format should be:
Storyboard:
Style(Unchanged): Realistic.
Subject: subject of the image based on the script;
Background: corresponding background content;
Behavior: Describes the character's current behavior；
===

Note that, each storyboard should be delimited by "===".
The script is as follows:
{script}

"""


class StoryBoard(Action):
    def __init__(self, llm=None):
        super().__init__()
        self.llm = llm
        if self.llm is None:
            self.llm = OpenAIGPTAPI()
        self.desc = "Based on the script, write text storyboard to create comics."

    def run(self, requirements, *args, **kwargs):
        scene_list = requirements[-1][0].split('Scene')
        response = []
        i = 0
        i2 = 0
        for scene in scene_list[1:]:
            i += 1
            storyboards = self.llm.aask(PREFIX_SETTINGS + OUTPUT_DESCRIPTION.format(script=scene))
            # print('###############PREFIX_SETTINGS OUTPUT_DESCRIPTION######################')
            storyboards_list = storyboards.split('Storyboard')
            for storyboard in storyboards_list[1:]:
                i2 += 1
                output = f'Storyboard {i2}:\n' + storyboard
                print('##########output#######:  \n', output)
                response.append(output)
            print('###############next######################')
            if i2 > 6:
                break
        return response
