"use client";

import React, {useState, useCallback, useEffect} from 'react';
import { Chat, Radio, RadioGroup} from '@douyinfe/semi-ui';
import io from 'socket.io-client';

// const defaultMessage = [
//     {
//         role: 'user',
//         id: '1',
//         createAt: 1715676751919,
//         content: [
//             {
//                 type: 'text',
//                 text: '这张图片里有什么？'
//             },
//             {
//                 type: 'image_url',
//                 image_url: {
//                     url: 'https://lf3-static.bytednsdoc.com/obj/eden-cn/ptlz_zlp/ljhwZthlaukjlkulzlp/root-web-sites/edit-bag.jpeg'
//                 }
//             }
//         ], 
//     },
//     {
//         role: 'assistant',
//         id: '2',
//         createAt: 1715676751919,
//         content: '图片中是一个有卡通画像装饰的黄色背包。'
//     },
//     {
//         role: 'user',
//         id: '3',
//         createAt: 1715676751919,
//         content: [
//             {
//                 type: 'text',
//                 text: '这张图片里有什么？'
//             },
//             {
//                 type: 'image_url',
//                 image_url: {
//                     url: 'https://lf3-static.bytednsdoc.com/obj/eden-cn/ptlz_zlp/ljhwZthlaukjlkulzlp/root-web-sites/edit-bag.jpeg'
//                 }
//             }
//         ], 
//     },
//     {
//         role: 'assistant',
//         id: '4',
//         createAt: 1715676751919,
//         content: '图片中是一个有卡通画像装饰的黄色背包。'
//     },
//     {
//         role: 'user',
//         id: '5',
//         createAt: 1715676751919,
//         content: [
//             {
//                 type: 'text',
//                 text: '这张图片里有什么？'
//             },
//             {
//                 type: 'image_url',
//                 image_url: {
//                     url: 'https://lf3-static.bytednsdoc.com/obj/eden-cn/ptlz_zlp/ljhwZthlaukjlkulzlp/root-web-sites/edit-bag.jpeg'
//                 }
//             }
//         ], 
//     },

// ];

const roleInfo = {
    user:  {
        name: 'User',
        avatar: 'https://registry.npmmirror.com/@lobehub/fluent-emoji-3d/1.1.0/files/assets/1f92f.webp'
    },
    assistant: {
        name: 'Assistant',
        avatar: 'https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcQxhMqeNZn_LVch21tE5__6bsGN_yl0XNHyfT6nFNHttWDhSILU',
    },
}


const commonOuterStyle = {
    // flexDirection: 'column' as const,
    border: '1px solid var(--semi-color-border)',
    borderRadius: '16px',
    margin: '8px 16px',
    height: '90vh',
    width: 'calc(90% - 32px)', // 考虑到左右margin
};

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
            console.log('Socket ID:', newSocket.id);
        });

        newSocket.on('connect_error', (error) => {
            console.error('Connection error:', error);
        });
        
        let currentStreamingMessage: any = null;

        newSocket.on('bot_response_start', (message) => {
        console.log(message);
        currentStreamingMessage = {
            role: 'assistant',
            id: getId(),
            createAt: Date.now(),
            content: '',
        }
        setMessages(prevMessages => [...prevMessages, {...currentStreamingMessage}]);
        });

        newSocket.on('bot_response_stream', (chunk) => {
            console.log('currentStreamingMessage', chunk);
            console.log('chunk', currentStreamingMessage);
            if (currentStreamingMessage) {
                currentStreamingMessage.content += chunk;
                setMessages(prevMessages => [...prevMessages.slice(0, -1), {...currentStreamingMessage}]);
            }
        });

        // newSocket.on('bot_response_end', (message) => {
        //     console.log('bot_response_end');
        //     currentStreamingMessage = null;
        // });

        return () => {
            console.log('Disconnecting from server');
            newSocket.disconnect();
        };
    }, []);

// const uploadProps = { action: uploadAction }
    const onChatsChange = useCallback((chats) => {
        setMessages(chats);
    }, []);


    const onMessageSend = useCallback((content: string) => {
        if (socket) {

            socket.emit('user_message', content);
        }
    }, [socket]);


    return (
            <Chat 
                align="leftRight"
                mode="bubble"
                topSlot={  
                    <div style={{ padding: '6px', borderBottom: '1px solid #e9e9e9', fontWeight: 'bold', color: '#000', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>  
                      Chat with MetaAgent
                    </div>  
                  }
                style={commonOuterStyle}
                chats={messages}
                roleConfig={roleInfo}
                onChatsChange={onChatsChange}
                onMessageSend={onMessageSend}
                // uploadProps={uploadProps}
            />
    )
}

export default DefaultChat;
