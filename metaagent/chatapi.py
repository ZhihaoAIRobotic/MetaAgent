
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
import uvicorn
import asyncio

app = FastAPI()
sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
socket_app = socketio.ASGIApp(sio, app)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许的源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")


@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")


@sio.on("user_message")
async def handle_message(sid, message):
    print(f"Received message from {sid}: {message}")
    # 这里可以添加你的聊天机器人逻辑
    # bot_response = f"Bot: I received your message: {message}"
    # await sio.emit("bot_response", bot_response, to=sid)


async def send_welcome_message(sid):
    welcome_message = "Bot: Welcome! How can I assist you today?"
    await sio.emit("bot_response", welcome_message, to=sid)


async def send_periodic_messages():
    while True:
        await asyncio.sleep(5)  # 每60秒发送一次消息
        periodic_message = "Bot: Just checking in. Do you need any help?"
        await sio.emit("bot_response", periodic_message)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(send_periodic_messages())


if __name__ == "__main__":
    uvicorn.run(socket_app, host="0.0.0.0", port=8000)
