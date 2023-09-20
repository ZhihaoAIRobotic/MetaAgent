from typing import Iterable
from jina import Executor, requests
from docarray import DocList
from metaagent.utils import get_class
from metaagent.actions.action import ActionOutput
from metaagent.models.openai_llm import OpenAIGPTAPI
from metaagent.logs import logger
from metaagent.information import Info
from metaagent.environment.env_info import EnvInfo
from metaagent.agents.agent_info import AgentInfo, InteractionInfo
from metaagent.agents.prompt_template import PREFIX_TEMPLATE, STATE_TEMPLATE，ACTION_DESCRIPTION


class Agent(Executor):
    def __init__(self, name="", profile="", goal="", constraints="", desc="", **kwargs):
        super().__init__(**kwargs)
        self._llm = OpenAIGPTAPI()
        self.agent_info = AgentInfo(name=name, profile=profile, goal=goal, constraints=constraints, desc=desc)
        self.all_states = []
        self.all_actions = []
        self.action_descs = ""
        self._role_id = f"{name}({profile})"
        self.todo = None  # action to do now
        self.state: int = 0  # index of action to do

    def _reset(self):
        self.all_states = []
        self.all_actions = []

    def _init_actions(self, actions: Iterable[str]):
        """Put actions into all_states and all_actions, and set prefix for actions."""
        self._reset()
        for idx, action_name in enumerate(actions):
            i = get_class(action_name)()
            i.set_prefix(self._get_prefix(), self.profile)
            self.action_descs += ACTION_DESCRIPTION.format(action_name=action_name, state=idx, desc=i.desc)
            self.all_actions.append(i)
            self.all_states.append(f"{idx}. {action_name}")

    def _watch(self, actions: Iterable[str]):
        """Watch the results by actions"""
        for i in actions:
            self.agent_info.watch_action_results.append(i)
        print('######################################')
        print(self.agent_info.watch_action_results)
        print('######################################')

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

    def _think(self) -> None:
        """Think for the next action"""
        if len(self.all_actions) == 1:
            # 如果只有一个动作，那就只能做这个
            self._set_state(0)
            return
        prompt = self._get_prefix()
        prompt += STATE_TEMPLATE.format(history=self.agent_info.history, states="\n".join(self.all_states),
                                        n_states=len(self.all_states) - 1, action_descriptions=self.action_descs)
        print(prompt)
        next_state = self._llm.aask(prompt)
        print('next_state', next_state)
        logger.debug(f"{prompt=}")
        if not next_state.isdigit() or int(next_state) not in range(len(self.all_states)):
            logger.warning(f'Invalid answer of state, {next_state=}')
            next_state = "0"
        self._set_state(int(next_state))

    def _act(self) -> Info:
        logger.info(f"{self._role_id}: ready to {self.todo}")
        # requirment = self.agent_info.important_memory.
        response = self.todo.run(self.agent_info.important_memory)
        if isinstance(response, ActionOutput):
            msg = Info(content=response.content, instruct_content=response.instruct_content, role=self.profile, cause_by=str(self.todo))
        else:
            msg = Info(content=response, role=self.profile, cause_by=str(self.todo))
        self.agent_info.memory.add(msg)
        return msg

    def _observe(self, env_info: EnvInfo) -> int:
        """从环境中观察，获得重要信息，并加入记忆"""

        env_msgs = env_info.env_memory.remember()
        
        observed = env_info.env_memory.remember_by_actions(self.agent_info.watch_action_results)
        
        self.agent_info.news = self.agent_info.memory.remember_news(observed)  # remember recent exact or similar memories

        for i in env_msgs:
            self.recv(i)

        news_text = [f"{i.role}: {i.content[:20]}..." for i in self.agent_info.news]
        if news_text:
            logger.debug(f'{self._role_id} observed: {news_text}')
        return len(self.agent_info.news)
    
    def _react(self) -> Info:
        """Think first, then do."""
        self._think()
        logger.debug(f"{self._role_id}: {self.state}, will do {self.todo}")
        return self._act()
    
    @requests
    def run(self, docs: DocList[InteractionInfo], **kwargs) -> DocList[InteractionInfo]:
        """观察，并基于观察的结果思考、行动"""
        # if agents_info.name == self.name:
        if self._role_id in [agent_info.role_id for agent_info in docs[0].agents_info]:
            for agent_info in docs[0].agents_info:
                if agent_info.role_id == self._role_id:
                    self.agent_info = agent_info
        else:
            docs[0].agents_info.append(self.agent_info)

        if not self._observe(docs[0].env_info):
            # if no news, do nothing
            logger.debug(f"{self._setting}: no news. waiting.")
            return

        rsp = self._react()
        # 将回复发布到环境，等待下一个订阅者处理
        print('rsp', rsp)
        docs[0].env_info.env_memory.add(rsp)
        docs[0].env_info.history += f"\n{rsp.Info_str}"

    def recv(self, msg: Info) -> None:
        """add message to memory."""
        if msg in self.agent_info.memory.remember():
            return
        self.agent_info.memory.add(msg)

    def handle(self, info: Info) -> Info:
        """接收信息，并用行动回复"""
        # logger.debug(f"{self.name=}, {self.profile=}, {message.role=}")
        self.recv(info)

        return self._react()