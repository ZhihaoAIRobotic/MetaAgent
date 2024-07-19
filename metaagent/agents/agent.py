from logs import LOGGER
import json

from LLMs.openai_llm import OpenAIGPTAPI
from actions.action_register import get_agent_action
from actions.action import Action
from prompts.agent_prompt import AGENT_TEMPLATE, ACTION_TEMPLATE


class Agent:
    def __init__(self, agent_goal, agent_actions, agent_example, **kwargs) -> None:
        self.profile = self.init_profile(agent_goal, agent_actions, agent_example)
        self._llm = OpenAIGPTAPI()
        self._vlm = None

    def init_profile(self, agent_goal, agent_actions, agent_example):
        return AGENT_TEMPLATE.format(agent_goal=agent_goal, agent_actions=agent_actions, agent_example=agent_example)

    def decision_making(self, observation: str):
        '''
        Hierachical decision making.
        High-level: select action.
        Low-level: generate parameters.
        '''
        action_selection_prompt = self.profile + observation
        print(action_selection_prompt)
        LOGGER.debug(action_selection_prompt)
        self.action, token_cost = self._llm.aask(action_selection_prompt)
        LOGGER.debug("****************Action****************/n")
        LOGGER.debug(self.action)

        try:
            start = self.action.find('{')
            end = self.action.rfind('}') + 1
            self.action = self.action[start:end]
            print(self.action)
            self.action = json.loads(self.action)
        except Exception:
            raise ValueError("The generated action is not in the correct format.")
        self.action = self.action['action']

        LOGGER.debug(self.action)
        self.action: Action = get_agent_action(self.action)()
        if self.action.params is None:
            self.action_params = None
            return 0
        action_params_prompt = ACTION_TEMPLATE.format(action=self.action.name, action_params=self.action.params, action_rules=self.action.rules, action_example=self.action.example)
        action_params_prompt = action_params_prompt + observation
        LOGGER.debug(action_params_prompt)
        self.action_params, token_cost = self._llm.aask(action_params_prompt)
        LOGGER.debug("****************ActionParam****************/n")
        LOGGER.debug(self.action_params)

        return 0

    def act(self):
        """Execute the action. params is a json string."""

        self.action(self.action_params)

    def step(self, observation: str):
        """Run the agent."""

        self.decision_making(observation)

        self.act()

        return 0
