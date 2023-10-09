from metaagent.LLMs.openai_llm import OpenAIGPTAPI
from metaagent.actions.action import Action

GOAL = """1. You will write a creative script based on the input prompt.
  2. First come up with characters, story background, dialogue between characters, etc.
  3. Your output serves a painting AI, which can only understand concrete descriptions rather than abstract concepts, and optimize the storyline based on your understanding of the painting AI."""

OUTPUT_DESCRIPTION = """
There is an example:

Characters:
1. Bob - A clumsy and well-meaning guy who always finds himself in hilarious situations.
2. Larry - Bob's best friend, who is witty and always ready with a sarcastic remark.
3. Emma - Bob's love interest, who is intelligent and has a great sense of humor.
4. Mr. Jenkins - Bob's grumpy boss, who is always annoyed by Bob's antics.
5. Mrs. Thompson - A quirky neighbor who is obsessed with her pet parrot, Polly.

Story Background:
Bob is an ordinary guy with an extraordinary talent for getting into trouble. He works at a boring office job under the watchful eye of his grumpy boss, Mr. Jenkins. Bob's life takes a hilarious turn when he meets Emma, a smart and funny woman who instantly captures his heart. With Larry by his side, Bob embarks on a series of misadventures that will leave the audience in stitches.

Scene 1: Bob's Office

Bob (tripping over his own feet): Oops! Sorry, Mr. Jenkins. I didn't mean to spill coffee all over your desk.
Mr. Jenkins (annoyed): Bob, you're a disaster waiting to happen. Can't you do anything right?

Scene 2: Bob's Apartment

Bob (excitedly): Larry, guess what? I met this amazing woman named Emma today. She's funny, smart, and beautiful!
Larry (sarcastically): Wow, Bob. I'm sure she'll be thrilled to be a part of your comedy of errors.

"Scene n:" is the necessarry text. The output script format should be as same as the example.

Now, for requirement:{user_input}. Please write a script for the user.
"""


class WriteScript(Action):
    def __init__(self, llm=None):
        super().__init__()
        self.llm = llm
        if self.llm is None:
            self.llm = OpenAIGPTAPI()
        self.desc = "Write script for the user."

    def run(self, requirements, *args, **kwargs):
        responses = []
        response = self.llm.aask(GOAL + OUTPUT_DESCRIPTION.format(user_input=requirements[-1]))
        responses.append(response)
        return responses
