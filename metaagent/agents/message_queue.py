import queue
import threading
import logging
from datetime import datetime


class MessageQueue:
    def __init__(self):
        self.queue = queue.Queue()
        self.lock = threading.Lock()
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='message_queue.log',
            filemode='a'
        )
        self.logger = logging.getLogger(__name__)

    def send_message(self, sender, recipient, message):
        with self.lock:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.queue.put((timestamp, sender, recipient, message))
            self.logger.info(f"Message sent: {sender} -> {recipient}: {message}")

    def receive_message(self, recipient):
        with self.lock:
            if not self.queue.empty():
                timestamp, sender, msg_recipient, message = self.queue.get()
                if msg_recipient == recipient:
                    self.logger.info(f"Message received: {sender} -> {recipient}: {message}")
                    return timestamp, sender, message
                else:
                    self.queue.put((timestamp, sender, msg_recipient, message))
            return None

    def get_queue_size(self):
        return self.queue.qsize()


# Example usage
if __name__ == "__main__":
    mq = MessageQueue()

    # Simulating multiple agents
    mq.send_message("Agent1", "Agent2", "Hello from Agent1")
    mq.send_message("Agent3", "Agent1", "Hello from Agent3")

    # Receiving messages
    message = mq.receive_message("Agent2")
    if message:
        print(f"Agent2 received: {message}")

    message = mq.receive_message("Agent1")
    if message:
        print(f"Agent1 received: {message}")

    print(f"Messages in queue: {mq.get_queue_size()}")