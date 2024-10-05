from typing import List, Dict
import tinydb
import asyncio

from metaagent.agents.message_queue import MessageQueue

from actions.action_register import get_agent_action
from actions.action import Action
from prompts.agent_prompt import ACTION_AGENT_TEMPLATE, EXAMPLE_TEMPLATE, CONVERSATIONAL_AGENT_TEMPLATE
from metaagent.logs import logger


class ConversationalAgent:
    def __init__(self, agent_name, db_name: str, llm = None, vlm = None, agent_goal=None, agent_example=None, agent_planner=None, **kwargs) -> None:
        self.agent_name = agent_name
        self.profile = self.init_profile(agent_goal, agent_example)
        self._llm = llm
        self._vlm = vlm
        if self._llm is None and self._vlm is None:
            logger.error("The agent should have a vlm or a language model.")
            raise ValueError("The agent should have a planner or a language model.")
        self.message_queue = None
        self.agent_state = None # running, waiting, stopped
        self.agent_planner = agent_planner

        # save agent info
        self.agent_info = {
            'agent_name': agent_name,
            'agent_goal': agent_goal,
            'agent_example': agent_example,
            'agent_planner': agent_planner,
            'agent_state': self.agent_state,
            'agent_profile': self.profile
        }
        self.receivers = {} # {action_name: [receiver_name]}
        self.short_memory = tinydb.TinyDB(db_name) # short memory is a tinyDB to store the conversation history

    def init_profile(self, agent_goal, agent_example):
        if agent_goal is None:
            agent_goal = 'I am a conversational agent.'
        if agent_example is None:
            agent_example = ''
        else:
            agent_example = EXAMPLE_TEMPLATE.format(example=agent_example)
        return CONVERSATIONAL_AGENT_TEMPLATE.format(agent_goal=agent_goal, agent_example=agent_example)

    async def step(self, observation):
        """Run the agent."""
        # WARNING: user or env should not send new message when agent is running in case messages between different agents is out of sync.
        # save the observation to short memory
        observation = {"content": observation, "role": "user"}
         
        # Get the existing document or create a new one if it doesn't exist
        doc = self.short_memory.get((tinydb.Query().sid == self.sid) & (tinydb.Query().agent_name == self.agent_name))
        if doc:
            history_observation = doc['observation']
        else:
            history_observation = []

        history_observation.append(observation)

        # delete the old observation 
        self.short_memory.remove((tinydb.Query().sid == self.sid) & (tinydb.Query().agent_name == self.agent_name))
 
        # get all the messages of the current sid and agent_name
        receivers = 'env'
        response = ''

        if self.agent_planner is not None:
            # TODO: implement the agent planner
            pass

        if self._llm is not None:
            async for result in self._llm.astream_completion(history_observation):
                await self.message_queue.send_message(self.agent_name, receivers, result)
                response = response + result

        elif self._vlm is not None:
            raise ValueError("To be implemented.")

        else:
            logger.error("The agent should have a planner or a language model.")
            raise ValueError("The agent should have a planner or a language model.")

        history_observation.append({"content": response, "role": "assistant"})
        logger.info(f"history_observation {history_observation}")

        # Update the existing document or insert a new one
        if doc:
            self.short_memory.update({'observation': history_observation}, 
                                     (tinydb.Query().sid == self.sid) & (tinydb.Query().agent_name == self.agent_name))
        else:
            self.short_memory.insert({'sid': self.sid, 'agent_name': self.agent_name, 'observation': history_observation})

    
    async def run(self, sid, message_queue):
        '''
        Run the agent.
        '''
        # WARNING: user or env should not send new message when agent is running in case messages between different agents is out of sync.
        self.sid = sid
        self.message_queue = message_queue
        logger.info(f"Agent {self.agent_name} is running.")
        while True:
            logger.info(f"in the session {sid}, Agent {self.agent_name} is running.")
            result = await self.message_queue.receive_message(self.agent_name)
            if result:
                timestamp, sender, observation = result
                await self.step(observation)


class SingleStepActionAgent:
    def __init__(self, agent_name, agent_goal, agent_actions, agent_example, message_queue: MessageQueue, agent_planner=None, **kwargs) -> None:
        self.agent_name = agent_name
        self.profile = self.init_profile(agent_goal, agent_actions, agent_example)
        self._llm = None
        self._vlm = None
        self.message_queue = message_queue
        self.agent_state = None # running, waiting, stopped
        self.agent_planner = agent_planner
        # save agent info
        self.agent_info = {
            'agent_name': agent_name,
            'agent_goal': agent_goal,
            'agent_actions': agent_actions,
            'agent_example': agent_example,
            'agent_profile': self.profile,
            'agent_planner': agent_planner,
            'agent_state': self.agent_state
        }
        self.route = {} # {action_name: [receiver_name]}

    def init_profile(self, agent_goal, agent_actions, agent_example):
        return ACTION_AGENT_TEMPLATE.format(agent_goal=agent_goal, agent_actions=agent_actions, agent_example=agent_example)

    async def decision_making(self, observation):
        action, action_params = await self.agent_planner.plan(self.agent_info, observation)
        return action, action_params

    async def act(self, action, action_params):
        """Execute the action. params is a json string."""
        return action(action_params)  

    async def astream_act(self, action, action_params):
        """Execute the action. params is a json string."""
        async for msg in action(action_params):
            yield msg

    async def step(self, observation):
        """Run the agent."""
        # WARNING: user or env should not send new message when agent is running in case messages between different agents is out of sync.
        action, action_params = await self.decision_making(observation)
        if action in self.route:
            receivers = self.route[action]
        else:
            receivers = ['env']

        for receiver in receivers:
            if hasattr(action, 'is_stream') and receiver == 'env':
                if action.is_stream:
                    async for result in self.astream_act(action, action_params):
                        await self.message_queue.send_message(self.agent_name, receivers, result)
                else:
                    results = await self.act(action, action_params)
                    await self.message_queue.send_message(self.agent_name, receivers, results)
            else:
                results = await self.act(action, action_params)
                await self.message_queue.send_message(self.agent_name, receivers, results)
    
    async def run(self):
        '''
        Run the agent.
        '''
        # ToDo: self.agent_state = 'running'
        # ToDo: while self.agent_state == 'running':
        # WARNING: user or env should not send new message when agent is running in case messages between different agents is out of sync.
        timestamp, sender, observation = await self.message_queue.receive_message(self.agent_name)
        await self.step(sender, observation)



