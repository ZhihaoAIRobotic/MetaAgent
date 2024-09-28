"use client";

import React, {useState, useCallback, useEffect} from 'react';
import { Chat, Radio, RadioGroup} from '@douyinfe/semi-ui';
import io from 'socket.io-client';

const defaultMessage = [
    // {
    //     role: 'user',
    //     id: '2',
    //     createAt: 1715676751919,
    //     content: "给一个 Semi Design 的 Button 组件的使用示例",
    // },
    // {
    //     role: 'assistant',
    //     id: '3',
    //     createAt: 1715676751919,
    //     content: "以下是一个 Semi 代码的使用示例：\n\`\`\`jsx \nimport React from 'react';\nimport { Button } from '@douyinfe/semi-ui';\n\nconst MyComponent = () => {\n  return (\n    <Button>Click me</Button>\n );\n};\nexport default MyComponent;\n\`\`\`\n",
    // }
];

const roleInfo = {
    user:  {
        name: 'User',
        avatar: 'https://lf3-static.bytednsdoc.com/obj/eden-cn/ptlz_zlp/ljhwZthlaukjlkulzlp/docs-icon.png'
    },
    assistant: {
        name: 'Assistant',
        avatar: 'https://lf3-static.bytednsdoc.com/obj/eden-cn/ptlz_zlp/ljhwZthlaukjlkulzlp/other/logo.png'
    },
}

const commonOuterStyle = {
    // display: 'flex',
    // flexDirection: 'column' as const,
    // border: '1px solid var(--semi-color-border)',
    // borderRadius: '16px',
    // margin: '8px 16px',
    height: '90vh',
    width: '100%',
    overflow: 'hidden',
}


let id = 0;
function getId() {
    return `id-${id++}`
}


function DefaultChat() {
    const [messages, setMessages] = useState<any[]>([]);
    const [socket, setSocket] = useState<Socket | null>(null);

    useEffect(() => {
        const newSocket = io('http://localhost:8000');
        setSocket(newSocket);

        newSocket.on('connect', () => {
            console.log('Connected to server');
        });

        newSocket.on('bot_response', (message) => {
            const newMessage = {
                role: 'assistant',
                id: getId(),
                createAt: Date.now(),
                content: message,
            };
            setMessages((prevMessages) => [...prevMessages, newMessage]);
        });

        return () => {
            newSocket.disconnect();
        };
    }, []);

    
    const onMessageSend = useCallback((content: string) => {
        if (socket) {
            const newUserMessage = {
                role: 'user',
                id: getId(),
                createAt: Date.now(),
                content: content,
            };
            setMessages((prevMessages) => [...prevMessages, newUserMessage]);
            socket.emit('user_message', content);
        }
    }, [socket]);


    return (
            <Chat 
                align="leftRight"
                mode="bubble"
                topSlot={  
                    <div style={{ padding: '6px', borderBottom: '1px solid #e9e9e9', fontWeight: 'bold', color: 'var(--semi-color-text-1)', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>  
                      Chat Title  
                    </div>  
                  }
                style={commonOuterStyle}
                chats={messages}
                roleConfig={roleInfo}
                onMessageSend={onMessageSend}
            />
    )
}

export default DefaultChat;
