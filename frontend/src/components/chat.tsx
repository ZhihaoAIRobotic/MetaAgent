'use client'

import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';

const WebSocketChat = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const socketRef = useRef();

  useEffect(() => {
    // 连接到WebSocket服务器
    socketRef.current = io('http://localhost:8000');

    // 监听来自服务器的消息
    socketRef.current.on('bot_response', (message) => {
      setMessages((prevMessages) => [...prevMessages, { text: message, from: 'bot' }]);
    });

    return () => {
      socketRef.current.disconnect();
    };
  }, []);

  const sendMessage = (e) => {
    e.preventDefault();
    if (inputMessage.trim() !== '') {
      // 发送消息到服务器
      socketRef.current.emit('user_message', inputMessage);
      setMessages((prevMessages) => [...prevMessages, { text: inputMessage, from: 'user' }]);
      setInputMessage('');
    }
  };

  return (
    <div className="flex flex-col h-screen">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`p-2 rounded-lg ${
              message.from === 'user' ? 'bg-blue-100 ml-auto' : 'bg-gray-100'
            }`}
          >
            {message.text}
          </div>
        ))}
      </div>
      <form onSubmit={sendMessage} className="p-4 border-t">
        <div className="flex">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            className="flex-1 border rounded-l-lg p-2"
            placeholder="Type your message..."
          />
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded-r-lg"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
};

export default WebSocketChat;
