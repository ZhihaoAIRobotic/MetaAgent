from typing import Iterable, List
from jina import Executor, requests
from docarray import DocList
from metaagent.LLMs.openai_llm import OpenAIGPTAPI
from metaagent.logs import logger
from metaagent.information import Info
from metaagent.environment.env_info import EnvInfo
from metaagent.agents.agent_info import AgentInfo, InteractionInfo
from metaagent.agents.prompt_template import PREFIX_TEMPLATE, STATE_TEMPLATE, ACTION_DESCRIPTION
from metaagent.actions import action_dict


class Agent(Executor):
    def __init__(self, id="", profile="", goal="", constraints="", actions: List = [], watch: List = [], **kwargs):
        super().__init__(**kwargs)
        self._llm = OpenAIGPTAPI()
        self.name = id
        self.agent_info = AgentInfo(name=id, profile=profile, goal=goal, constraints=constraints)
        self.all_states = []
        self.all_actions = []
        self._role_id = f"{id}({profile})"
        self.todo = None  # action to do now
        self.state: int = 0  # index of action to do
        self.action_descs = ''
        self._init_actions(actions)
        self._watch(watch)

    def _reset(self):
        self.all_states = []
        self.all_actions = []

    def _init_actions(self, actions: Iterable[str]):
        """Put actions into all_states and all_actions, and set prefix for actions."""
        self._reset()
        for idx, action_name in enumerate(actions):
            # print(action_name)
            i = action_dict[action_name]()
            self.action_descs += ACTION_DESCRIPTION.format(action_name=action_name, state=idx, desc=i.desc)
            # i.set_prefix(self._get_prefix(), self.profile)
            self.all_actions.append(i)
            self.all_states.append(f"{idx}. {action_name}")

    def _watch(self, actions: Iterable[str]):
        """Watch the results by actions"""
        for i in actions:
            self.agent_info.watch_action_results.append(i)

    def _set_state(self, state):
        """Update the current state."""
        self.state = state
        logger.debug(self.all_actions)
        self.todo = self.all_actions[self.state]

    @property
    def profile(self):
        return self.agent_info.profile

    def _get_prefix(self):
        """Get the prefix of the agent."""
        return PREFIX_TEMPLATE.format(**self.agent_info.dict())

    def plan(self) -> None:
        """Think for the next action"""
        if len(self.all_actions) == 1:
            self._set_state(0)
            return
        prompt = self._get_prefix()
        prompt += STATE_TEMPLATE.format(history=self.agent_info.history, states="\n".join(self.all_states),
                                        n_states=len(self.all_states) - 1, action_descriptions=self.action_descs)
        # print(prompt)
        next_state = self._llm.aask(prompt)
        # print('next_state', next_state)
        logger.debug(f"{prompt=}")
        if not next_state.isdigit() or int(next_state) not in range(len(self.all_states)):
            logger.warning(f'Invalid answer of state, {next_state=}')
            next_state = "0"
        self._set_state(int(next_state))

    def act(self) -> Info:
        logger.info(f"{self._role_id}: ready to {self.todo}")
        response = self.todo.run(self.agent_info.important_memory)
        msg = Info(content=response, agent_id=id, role=self.profile, cause_by=str(self.todo))
        print('######################################')
        print(msg)
        self.agent_info.memory.add(msg)
        return msg

    def _observe(self, env_info: EnvInfo) -> int:
        # print(env_info)

        env_msgs = env_info.env_memory.remember()
        
        observed = env_info.env_memory.remember_by_actions(self.agent_info.watch_action_results)
        
        self.agent_info.news = self.agent_info.memory.remember_news(observed)  # remember recent exact or similar memories

        for i in env_msgs:
            self.recv(i)

        news_text = [f"{i.role}: {i.content[:20]}..." for i in self.agent_info.news]
        if news_text:
            logger.debug(f'{self._role_id} observed: {news_text}')
        return len(self.agent_info.news)
    
    def step(self) -> Info:
        self.plan()
        logger.debug(f"{self._role_id}: {self.state}, will do {self.todo}")
        return self.act()
    
    @requests
    def run(self, docs: DocList[InteractionInfo], **kwargs) -> DocList[InteractionInfo]:
        if self._role_id in [agent_info.role_id for agent_info in docs[0].agents_info]:
            for agent_info in docs[0].agents_info:
                if agent_info.role_id == self._role_id:
                    self.agent_info = agent_info
        else:
            docs[0].agents_info.append(self.agent_info)

        if not self._observe(docs[0].env_info):
            logger.debug("no news. waiting.")
            return

        rsp = self.step()
        # print('rsp', rsp)
        docs[0].env_info.env_memory.add(rsp)
        docs[0].env_info.history += f"\n{rsp.Info_str}"

    def recv(self, msg: Info) -> None:
        if msg in self.agent_info.memory.remember():
            return
        self.agent_info.memory.add(msg)

    def handle(self, info: Info) -> Info:
        self.recv(info)
        return self.step()
