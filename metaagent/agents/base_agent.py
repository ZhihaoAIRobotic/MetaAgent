
from __future__ import annotations

from typing import Iterable, Type

from pydantic import BaseModel, Field

# from metagpt.environment import Environment
from metaagent.config import CONFIG
from metaagent.actions.action import Action, ActionOutput
from metaagent.models.openai_llm import OpenAIGPTAPI
from metaagent.logs import logger
from metaagent.memory.shortterm_memory import Memory
from metaagent.memory.longterm_memory import LongTermMemory
from metaagent.information import Message

from metaagent.agents.prompt_template import PREFIX_TEMPLATE, STATE_TEMPLATE, ROLE_TEMPLATE 


class RoleSetting(BaseModel):
    """角色设定"""
    name: str
    profile: str
    goal: str
    constraints: str
    desc: str

    def __str__(self):
        return f"{self.name}({self.profile})"

    def __repr__(self):
        return self.__str__()


class RoleContext(BaseModel):
    """角色运行时上下文"""
    # name: str
    env: 'Environment' = Field(default=None)
    memory: Memory = Field(default_factory=Memory)
    long_term_memory: LongTermMemory = Field(default_factory=LongTermMemory)
    state: int = Field(default=0)
    todo: Action = Field(default=None)
    watch: set[Type[Action]] = Field(default_factory=set)
    # news: list[Type[Message]] = Field(default=[])

    class Config:
        arbitrary_types_allowed = True

    def check(self, role_id: str):
        if hasattr(CONFIG, "long_term_memory") and CONFIG.long_term_memory:
            self.long_term_memory.recover_memory(role_id, self)
            self.memory = self.long_term_memory  # use memory to act as long_term_memory for unify operation

    @property
    def important_memory(self) -> list[Message]:
        """获得关注动作对应的信息"""
        return self.memory.get_by_actions(self.watch)

    @property
    def history(self) -> list[Message]:
        return self.memory.get()


class Agent:
    """角色/代理"""

    def __init__(self, name="", profile="", goal="", constraints="", desc=""):
        self._llm = OpenAIGPTAPI()
        self._setting = RoleSetting(name=name, profile=profile, goal=goal, constraints=constraints, desc=desc)
        self._states = []
        self._actions = []
        self._role_id = str(self._setting)
        self._rc = RoleContext()

    def _reset(self):
        self._states = []
        self._actions = []

    def _init_actions(self, actions):
        self._reset()
        for idx, action in enumerate(actions):
            if not isinstance(action, Action):
                i = action("")
            else:
                i = action
            i.set_prefix(self._get_prefix(), self.profile)
            self._actions.append(i)
            self._states.append(f"{idx}. {action}")

    def _watch(self, actions: Iterable[Type[Action]]):
        """监听对应的行为"""
        self._rc.watch.update(actions)
        # check RoleContext after adding watch actions
        self._rc.check(self._role_id)

    def _set_state(self, state):
        """Update the current state."""
        self._rc.state = state
        logger.debug(self._actions)
        self._rc.todo = self._actions[self._rc.state]

    def set_env(self, env: 'Environment'):
        """设置角色工作所处的环境，角色可以向环境说话，也可以通过观察接受环境消息"""
        self._rc.env = env

    @property
    def profile(self):
        """获取角色描述（职位）"""
        return self._setting.profile

    def _get_prefix(self):
        """获取角色前缀"""
        if self._setting.desc:
            return self._setting.desc
        return PREFIX_TEMPLATE.format(**self._setting.dict())

    async def _think(self) -> None:
        """思考要做什么，决定下一步的action"""
        if len(self._actions) == 1:
            # 如果只有一个动作，那就只能做这个
            self._set_state(0)
            return
        prompt = self._get_prefix()
        prompt += STATE_TEMPLATE.format(history=self._rc.history, states="\n".join(self._states),
                                        n_states=len(self._states) - 1)
        next_state = await self._llm.aask(prompt)
        logger.debug(f"{prompt=}")
        if not next_state.isdigit() or int(next_state) not in range(len(self._states)):
            logger.warning(f'Invalid answer of state, {next_state=}')
            next_state = "0"
        self._set_state(int(next_state))

    async def _act(self) -> Message:
        # prompt = self.get_prefix()
        # prompt += ROLE_TEMPLATE.format(name=self.profile, state=self.states[self.state], result=response,
        #                                history=self.history)

        logger.info(f"{self._setting}: ready to {self._rc.todo}")
        response = await self._rc.todo.run(self._rc.important_memory)
        # logger.info(response)
        if isinstance(response, ActionOutput):
            msg = Message(content=response.content, instruct_content=response.instruct_content,
                          role=self.profile, cause_by=type(self._rc.todo))
        else:
            msg = Message(content=response, role=self.profile, cause_by=type(self._rc.todo))
        self._rc.memory.add(msg)
        # logger.debug(f"{response}")

        return msg

    async def _observe(self) -> int:
        """从环境中观察，获得重要信息，并加入记忆"""
        if not self._rc.env:
            return 0
        env_msgs = self._rc.env.memory.get()
        
        observed = self._rc.env.memory.get_by_actions(self._rc.watch)
        
        self._rc.news = self._rc.memory.remember(observed)  # remember recent exact or similar memories

        for i in env_msgs:
            self.recv(i)

        news_text = [f"{i.role}: {i.content[:20]}..." for i in self._rc.news]
        if news_text:
            logger.debug(f'{self._setting} observed: {news_text}')
        return len(self._rc.news)

    def _publish_message(self, msg):
        """如果role归属于env，那么role的消息会向env广播"""
        if not self._rc.env:
            # 如果env不存在，不发布消息
            return
        self._rc.env.publish_message(msg)

    async def _react(self) -> Message:
        """先想，然后再做"""
        await self._think()
        logger.debug(f"{self._setting}: {self._rc.state=}, will do {self._rc.todo}")
        return await self._act()

    def recv(self, message: Message) -> None:
        """add message to history."""
        # self._history += f"\n{message}"
        # self._context = self._history
        if message in self._rc.memory.get():
            return
        self._rc.memory.add(message)

    async def handle(self, message: Message) -> Message:
        """接收信息，并用行动回复"""
        # logger.debug(f"{self.name=}, {self.profile=}, {message.role=}")
        self.recv(message)

        return await self._react()

    async def run(self, message=None):
        """观察，并基于观察的结果思考、行动"""
        if message:
            if isinstance(message, str):
                message = Message(message)
            if isinstance(message, Message):
                self.recv(message)
            if isinstance(message, list):
                self.recv(Message("\n".join(message)))
        elif not await self._observe():
            # 如果没有任何新信息，挂起等待
            logger.debug(f"{self._setting}: no news. waiting.")
            return

        rsp = await self._react()
        # 将回复发布到环境，等待下一个订阅者处理
        self._publish_message(rsp)
        return rsp
    

