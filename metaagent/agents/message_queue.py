from typing import List
import asyncio

from datetime import datetime

from MetaAgent.metaagent.simple_logger import logger


class MessageQueue:
    # TODO: Add message id for each message to support dividing messages into different sessions in the user interface
    def __init__(self, receivers: List[str] = None):
        if receivers is None:
            self.receivers = ['env']
        elif 'env' not in receivers:
            receivers.append('env')
            self.receivers = receivers
        else:
            self.receivers = receivers
        self.queue = {}
        # every receiver has its own queue
        for receiver in self.receivers:
            self.queue[receiver] = asyncio.Queue()

    async def send_message(self, sender, recipient: str, message): # TODO: add message id
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await self.queue[recipient].put((timestamp, sender, recipient, message)) # TODO: add message id

    async def astream_receive_message(self, recipient):
        # while not self.queue[recipient].empty():
            # to prevent the message being unconsistently received by different agents
            # Lock the queue to prevent concurrent access
        timestamp, sender, msg_recipient, message = await self.queue[recipient].get()
        if msg_recipient == recipient:
            # logger.info(f"Message received: {sender} -> {recipient}: {message}")
            yield timestamp, sender, message
        else:
            logger.error("Message received by wrong recipient")
            raise Exception("Message received by wrong recipient")

    async def receive_message(self, recipient):
        # logger.error(f"receive_message: {recipient}")
        # while not self.queue[recipient].empty():
        timestamp, sender, msg_recipient, message = await self.queue[recipient].get()
        if msg_recipient == recipient:
                # logger.info(f"Message received: {sender} -> {recipient}: {message}")
            return timestamp, sender, message
        else:
            logger.error("Message received by wrong recipient")
            raise Exception("Message received by wrong recipient")

    async def get_queue_size(self):
        return self.queue.qsize()
    
    async def cleanup(self):
        for receiver in self.receivers:
            while not self.queue[receiver].empty():
                await self.queue[receiver].get()


# class SharedMessageQueue:

