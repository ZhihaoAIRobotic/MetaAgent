from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
import uvicorn
import asyncio
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from MetaAgent.metaagent.manager import AgentManager
from metaagent.agents.agent import ConversationalAgent
from metaagent.llms.llmapi import LLM_API
from metaagent.logs import logger

class ChatAPI:
    def __init__(self):
        self.app = FastAPI()
        self.sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
        self.socket_app = socketio.ASGIApp(self.sio, self.app)

        self.manager = AgentManager()
        agent = ConversationalAgent(self.manager.message_queue, 'ConversationalAgent', 'chatdb.json')
        deepseek = LLM_API("deepseek/deepseek-chat")
        agent._llm = deepseek
        self.manager.add_agent(agent)
        self.setup_cors()
        self.setup_socket_events()
        self.setup_startup_event()

    def setup_cors(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def setup_socket_events(self):
        @self.sio.event
        async def connect(sid, environ):
            print(f"Client connected: {sid}")

        @self.sio.event
        async def disconnect(sid):
            print(f"Client disconnected: {sid}")

        @self.sio.on("user_message")
        async def handle_message(sid, message):
            logger.info(sid)
            await self.sio.emit('bot_response_start', 'Bot: Hi, I am a conversational agent. How can I help you?', to=sid)

            response =  self.manager.astream_interact_with_env(sid, message, 'ConversationalAgent')
            async for timestamp, sender, response in response:
                logger.error(f"debugger: {timestamp}, {response}")
                await self.sio.emit("bot_response_stream", response)

    def setup_startup_event(self):
        @self.app.on_event("startup")
        async def startup_event():
            asyncio.create_task(self.send_periodic_messages())

    async def send_periodic_messages(self):
        while True:
            await asyncio.sleep(50)
            periodic_message = "Bot: Just checking in. Do you need any help?"
            await self.sio.emit("bot_response", periodic_message)

    def run(self):
        uvicorn.run(self.socket_app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    chat_api = ChatAPI()
    chat_api.run()

    agent = ConversationalAgent(self.manager.message_queue, 'ConversationalAgent', 'chatdb.json')
    deepseek = LLM_API("deepseek/deepseek-chat")
    agent._llm = deepseek
    self.manager.add_agent(agent)
