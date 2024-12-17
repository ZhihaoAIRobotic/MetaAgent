'''
control the interaction between agents, users and environments
'''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
import uvicorn
import asyncio
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from metaagent.agents.message_queue import MessageQueue
from metaagent.llms.llmapi import LLM_API
from metaagent.logs import logger
from metaagent.agents.agent import ConversationalAgent


class AgentManager:
    def __init__(self):
        
        # initialize user defined variables
        self.agents_class = []
        self.agent_name = []
        self.agent_llm = []
        self.agents_interact_with_env = None

        # initialize variables
        self._agents_tasks = None
        self._monitor_task = None
        
        # initialize user session manager dict
        self.user_sessions = {}

        # initialize FastAPI and SocketIO
        self.app = FastAPI()
        self.sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
        self.socket_app = socketio.ASGIApp(self.sio, self.app)

        self.setup_cors()
        self.setup_socket_events()
        self.setup_startup_agent()

    def add_agent(self, agent_class, db_name, agent_name, agent_llm=None, agent_vlm=None, agent_config=None):
        '''
        Add agent to the manager by agent code
        '''
        self.agents_class.append(agent_class) 
        self.agent_name.append(agent_name)

        self.db_name = db_name

        if agent_llm:
            self.agent_llm.append(agent_llm)
        if agent_vlm:
            self.agent_llm.append(agent_vlm)
        if agent_llm is None and agent_vlm is None:
            deepseek = LLM_API("deepseek/deepseek-chat")
            self.agent_llm.append(deepseek)
        if agent_config:
            # TODO: load agent from agent_config
            pass

    def set_agents_interact_with_env(self, agent_name):
        self.agents_interact_with_env = agent_name

    def load_agent(self, agent_config):
        '''
        Load agent by agent config
        '''
        self.agent_config = agent_config
        # TODO: load agent from agent_config

    def check_setup(self):
        if not self.agents_class:
            raise Exception("No agent added to the manager")
        if not self.agents_interact_with_env:
            raise Exception("No agents interact with env")
        

    async def send_message_to_chat_ui(self, sid):
        # logger.debug(f"session: {sid}")
        session = self.user_sessions[sid]
        # logger.error(f"session: {sid}")
        session_message_queue = session['message_queue']
        while True:
            async for timestamp, sender, response in session_message_queue.astream_receive_message('env'):
                await self.sio.emit("bot_response_stream", response, to=sid)
            await asyncio.sleep(0.05)

    def setup_socket_events(self):
        @self.sio.event
        async def connect(sid, environ):
            print(f"New connection: {sid}")
            receivers = ['env']
            # Agent should be defined here
            self.agents = []
            
            for i, agent_class in enumerate(self.agents_class):
                agent = agent_class(self.agent_name[i], self.db_name, self.agent_llm[i])
                self.agents.append(agent)
            for agent in self.agents:
                receivers.append(agent.agent_name)
            
            mq = MessageQueue(receivers)
            self.user_sessions[sid] = {
                'message_queue': mq,
                'task': [asyncio.create_task(agent.run(sid, mq)) for agent in self.agents]
            }
            asyncio.create_task(self.send_message_to_chat_ui(sid))

        @self.sio.event
        async def disconnect(sid):
            print(f"Disconnected: {sid}")
            if sid in self.user_sessions:  
                for task in self.user_sessions[sid]['task']:  
                    task.cancel()
                
                # wait for task to finish processing
                for task in self.user_sessions[sid]['task']:  
                    try:  
                        await task  
                    except asyncio.CancelledError:  
                        pass
                # clean MessageQueue to ensure no memory leaks
                await self.user_sessions[sid]['message_queue'].cleanup()  
                # remove session from user_sessions
                del self.user_sessions[sid] 

        @self.sio.on("user_message")
        async def handle_message(sid, message):
            logger.info(f'sid and message: {sid}: {message}')
            # add 
            await self.sio.emit('bot_response_start', 'start', to=sid)
            send_msg_task = asyncio.create_task(self.user_sessions[sid]['message_queue'].send_message('env', self.agents_interact_with_env, message))
            await send_msg_task

    def setup_startup_agent(self):
        @self.app.on_event("startup")
        async def startup_event():
            self.check_setup()
            # await task

    def setup_cors(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def run(self):
        uvicorn.run(self.socket_app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    chat_api = AgentManager()

    agent_name = 'ConversationalAgent'
    db_name = 'conversational_agent_db'
    agent_llm = LLM_API("deepseek/deepseek-chat")

    chat_api.add_agent(ConversationalAgent, db_name, agent_name, agent_llm)
    chat_api.set_agents_interact_with_env('ConversationalAgent')

    chat_api.run()
