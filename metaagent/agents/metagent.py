from copy import deepcopy
from typing import Iterable, Dict, List, Optional, Union
from jina import Executor, requests
from docarray import DocList
from metaagent.utils import get_class
# from metagpt.environment import Environment
from metaagent.actions.action import ActionOutput
from metaagent.models.openai_llm import OpenAIGPTAPI
from metaagent.logs import logger
from metaagent.information import Info
from metaagent.agents.base_agent import Metagent
from metaagent.environment.env_info import EnvInfo
from metaagent.agents.agent_info import AgentInfo, InteractionInfo
from metaagent.agents.prompt_template import PREFIX_TEMPLATE, STATE_TEMPLATE, ROLE_TEMPLATE
from metaagent.agents.retrieve import KnowledgeRetrieval


class MyAgent(Metagent):
    """"
        to do: add mutli_actions inference
    """
    def __init__(self,
            multi_actions: Optional[MultiActions] = None,
            knowledge_retrieval: Optional[KnowledgeRetrieval] = None,   
            **kwargs):
        super(MyAgent).__init__(**kwargs)

        self._llm = self._llm
        self.agent_info = self.agent_info
        self.all_states = self.all_states
        self.all_actions = multi_actions
        self._role_id = self._role_id 
        self.todo = None  # action to do now
        self.state: int = 0  # index of action to do

        self.knowledge_retrieval = knowledge_retrieval
        self.prompt_max_length= 1000
        self.reset()

    def get_knowledge(self, query: str) -> List[str]:
        """retrieve knowledge given query

        Args:
            query (str): query

        """
        return self.knowledge_retrieval.retrieve(
            query) if self.knowledge_retrieval else []
    
    def get_knowledge_str(self, knowledge_list):
        """generate knowledge string

        Args:
            knowledge_list (List[str]): list of knowledges

        """
        sep ="\n\n"
        knowledge = sep.join(
            [f'{i+1}. {k}' for i, k in enumerate(knowledge_list)])
        knowledge_str = f'{sep}Web search results: {sep}{knowledge}' if len(
            knowledge_list) > 0 else ''
        return knowledge_str

    def get_history_str(self, prompt):
        """generate history string
        """
        history_str = ''
        
        sep="\n\n"
        for i in range(len(self.agent_info.history)):
            history_item = self.agent_info.history[len(self.agent_info.history) - i - 1]
            text = history_item

            if len(history_str) + len(text) + \
                    len(prompt) > self.prompt_max_length:
                break
            history_str = f'{sep}{text.strip()}{history_str}'

        return history_str
    
    # initialize prompts, the first round without extra history
    def _init_prompt(self)->str:
        # role description
        prompt = self._get_prefix()
        return prompt
    
    # 根据历史信息和现有对话来更新prompt的history和state
    def _update_prompts(self)->str:
        """
        todo: add user dialogue history to prompt
        """
        prompt = self._init_prompt()
        history_str = self.get_history_str(prompt)

        # obtain useful knowledge
        knowledge_str = self.get_knowledge_str(self.agent_info.news)
        # state_template 
        prompt += STATE_TEMPLATE.format(history=history_str, states="\n".join(self.all_states),
                                        n_states=len(self.all_states) - 1, knowledge=knowledge_str)
        # current user input information
        prompt += f"user input: '{self.agent_info.news}'. "

        return prompt
    
    
    def _think(self) -> None:
        """Think for the next action"""
        if len(self.all_actions) == 1:
            # 如果只有一个动作，那就只能做这个
            self._set_state(0)
            return
        
        prompt = self._update_prompts()       

        next_state = self._llm.aask(prompt)
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
        """先想，然后再做"""
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
        docs[0].env_info.env_memory.add(rsp)
        docs[0].env_info.history += f"\n{rsp.Info_str}"