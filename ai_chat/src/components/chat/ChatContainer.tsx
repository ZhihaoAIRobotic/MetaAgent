import { BotAvatar } from "@/components/chat/BotAvatar";
import { BotMsgBox } from "@/components/chat/BotMsgBox";
import { UserMsgBox } from "@/components/chat/UserMsgBox";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PaperPlaneIcon } from "@radix-ui/react-icons";
const botid = 2;

export const ChatContainer = () => {
  return (
    <div className="relative rounded-md shadow-lg w-full max-w-2xl h-screen bg-gray-400/20 overflow-y-scroll">
      <div className="w-full h-60 sticky top-0 backdrop-blur-sm shadow-sm py-5">
        <BotAvatar />
      </div>
      <div className="flex flex-col space-y-2 pt-5 pb-24 px-10 ">
        {chat.map((msg, index) => {
          const { message, time, senderId, feedback } = msg;
          if (msg.senderId === botid) {
            return <BotMsgBox msg={message} />;
          }
          return <UserMsgBox msg={message} />;
        })}
      </div>
      <div className="h-20 w-full max-w-2xl items-center flex space-x-2 px-4 fixed bottom-0 bg-black/10 shadow-sm backdrop-blur-sm">
        <Input type="text" className="h-12" />
        <Button type="submit" className="px-2 py-2 h-fit">
          <PaperPlaneIcon className="w-6 h-6" />
        </Button>
      </div>
      {/* inputbox */}
    </div>
  );
};

const chat = [
  {
    message: "Hi",
    time: "Mon Dec 10 2018 07:45:00 GMT+0000 (GMT)",
    senderId: 11,
    feedback: {
      isSent: true,
      isDelivered: true,
      isSeen: true,
    },
  },
  {
    message: "Hello. How can I help You?",
    time: "Mon Dec 11 2018 07:45:15 GMT+0000 (GMT)",
    senderId: 2,
    feedback: {
      isSent: true,
      isDelivered: true,
      isSeen: true,
    },
  },
  {
    message: "Can I get details of my last transaction I made last month? 🤔",
    time: "Mon Dec 11 2018 07:46:10 GMT+0000 (GMT)",
    senderId: 11,
    feedback: {
      isSent: true,
      isDelivered: true,
      isSeen: true,
    },
  },
  {
    message: "We need to check if we can provide you such information.",
    time: "Mon Dec 11 2018 07:45:15 GMT+0000 (GMT)",
    senderId: 2,
    feedback: {
      isSent: true,
      isDelivered: true,
      isSeen: true,
    },
  },
  {
    message: "I will inform you as I get update on this.",
    time: "Mon Dec 11 2018 07:46:15 GMT+0000 (GMT)",
    senderId: 2,
    feedback: {
      isSent: true,
      isDelivered: true,
      isSeen: true,
    },
  },
  {
    message: "We need to check if we can provide you such information.",
    time: "Mon Dec 11 2018 07:45:15 GMT+0000 (GMT)",
    senderId: 2,
    feedback: {
      isSent: true,
      isDelivered: true,
      isSeen: true,
    },
  },
  {
    message: "I will inform you as I get update on this.",
    time: "Mon Dec 11 2018 07:46:15 GMT+0000 (GMT)",
    senderId: 2,
    feedback: {
      isSent: true,
      isDelivered: true,
      isSeen: true,
    },
  },
  {
    message: "We need to check if we can provide you such information.",
    time: "Mon Dec 11 2018 07:45:15 GMT+0000 (GMT)",
    senderId: 11,
    feedback: {
      isSent: true,
      isDelivered: true,
      isSeen: true,
    },
  },
  {
    message: "I will inform you as I get update on this.",
    time: "Mon Dec 11 2018 07:46:15 GMT+0000 (GMT)",
    senderId: 2,
    feedback: {
      isSent: true,
      isDelivered: true,
      isSeen: true,
    },
  },
  {
    message: "We need to check if we can provide you such information.",
    time: "Mon Dec 11 2018 07:45:15 GMT+0000 (GMT)",
    senderId: 11,
    feedback: {
      isSent: true,
      isDelivered: true,
      isSeen: true,
    },
  },
  {
    message: "I will inform you as I get update on this.",
    time: "Mon Dec 11 2018 07:46:15 GMT+0000 (GMT)",
    senderId: 2,
    feedback: {
      isSent: true,
      isDelivered: true,
      isSeen: true,
    },
  },
  {
    message: "We need to check if we can provide you such information.",
    time: "Mon Dec 11 2018 07:45:15 GMT+0000 (GMT)",
    senderId: 2,
    feedback: {
      isSent: true,
      isDelivered: true,
      isSeen: true,
    },
  },
  {
    message: "I will inform you as I get update on this.",
    time: "Mon Dec 11 2018 07:46:15 GMT+0000 (GMT)",
    senderId: 2,
    feedback: {
      isSent: true,
      isDelivered: true,
      isSeen: true,
    },
  },
  {
    message: "We need to check if we can provide you such information.",
    time: "Mon Dec 11 2018 07:45:15 GMT+0000 (GMT)",
    senderId: 11,
    feedback: {
      isSent: true,
      isDelivered: true,
      isSeen: true,
    },
  },
  {
    message: "I will inform you as I get update on this.",
    time: "Mon Dec 11 2018 07:46:15 GMT+0000 (GMT)",
    senderId: 2,
    feedback: {
      isSent: true,
      isDelivered: true,
      isSeen: true,
    },
  },
  {
    message: "We need to check if we can provide you such information.",
    time: "Mon Dec 11 2018 07:45:15 GMT+0000 (GMT)",
    senderId: 2,
    feedback: {
      isSent: true,
      isDelivered: true,
      isSeen: true,
    },
  },
  {
    message: "I will inform you as I get update on this.",
    time: "Mon Dec 11 2018 07:46:15 GMT+0000 (GMT)",
    senderId: 2,
    feedback: {
      isSent: true,
      isDelivered: true,
      isSeen: true,
    },
  },
];
