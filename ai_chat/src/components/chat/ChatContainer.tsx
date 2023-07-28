import { BotAvatar } from "@/components/chat/BotAvatar";
import { BotMsgBox } from "@/components/chat/BotMsgBox";
import { UserMsgBox } from "@/components/chat/UserMsgBox";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PaperPlaneIcon } from "@radix-ui/react-icons";
import { format, isSameDay } from "date-fns";
import { SubmitHandler, useForm} from "react-hook-form";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
} from "@/components/ui/form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useLocalStorage } from "@react-hooks-library/core";
import { useMemo } from "react";


 /**
  * todo:
  * chat feedback
  * 
  * avatar images
  */
// temp data
const doamin = "http://localhost:3000/api";
// const doamin = "http://region-46.seetacloud.com:27604";
// const doamin = "http://region-3.seetacloud.com:57942";

const userId = 0;
// curl --request POST 'http://region-46.seetacloud.com:27604/chat' --header 'Content-Type: application/json' -d '{"data": [{"text": "hallo,who are you"}], "parameters": {"param1": "hello world"}}'

const FormSchema = z.object({
  message: z.string().min(1),
});

type Chat = {
  message: string;
  createAt: number;
  blob?: string;
  senderId: number;
}
type ResponseChat = {
  text: string;
  blob?: string;
};
type Response = {
    data: ResponseChat[];
}

export const ChatContainer = () => {
  const [state, setValue] = useLocalStorage("chat","");
  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      message: '',
    }
  });

  const onSubmit: SubmitHandler<z.infer<typeof FormSchema>> = async (
    data
  ) => {

    const { message } = data;
    const newChat = {
      message,
      createAt: Date.now(),
      senderId: userId,
    };


   const res = await fetchChat(message);
   const newChatList = [...chat, newChat,res];

   setValue(JSON.stringify(newChatList));
   return;
  };

  const fetchChat = async (msg: string) => {
    try {
      
      const testDo= "/hello"
      const res = await fetch(`${doamin}/chat`, {
        method: "POST",
        headers: new Headers({
          "Content-Type": "application/json",
        }),
        body: JSON.stringify({
          data: [{ text: msg }],
        }),
      })
      .then(res => res.json())
      .then(data => {

        console.log("data",data);
        const { data: chatRes } = data;
        const { text ,blob} = chatRes[0];
        const newChat = {
          message: text,
          blob,
          createAt: Date.now(),
          senderId: 1,
        };
        const newChatList = [...chat, newChat];
        return newChat;
        // setValue(JSON.stringify(newChatList));

      }).catch((err) => {
        console.log("error: ",err)
      });
      
      return res;
    } catch (err) {
      console.log(err);
    }
  };

  const chat = useMemo(() => {
    return state ? JSON.parse(state) as Chat[] : [];
  },[state]);

  const getDate = (current: Date, previous?: Date) => {
    if (!previous || !isSameDay(current, previous)) {
      return(
        <div className="text-center text-gray-400 text-xs py-2">
          {format(current, "dd MMMM yyyy")}
        </div>
      );
    }

   return null;
  };

  return (
    <div className="relative rounded-md shadow-lg w-full max-w-2xl h-screen bg-gray-400/20 overflow-y-scroll scrollbar scrollbar-thumb-gray-900 scrollbar-track-gray-100">
      {/* Avatar */}
      <div className="w-full h-60 sticky top-0 backdrop-blur-sm shadow-sm py-5">
        <BotAvatar />
      </div>

      {/* Message Container */}
      <div className="space-y-4 pt-5 pb-24 px-10 ">
        {chat.map((msg, index) => {
          const { message } = msg;
          const msgTime = new Date(msg.createAt);
          const prevTime = chat[(index - 1)]
            ? new Date(chat[index - 1]?.createAt)
            : undefined;
          return (
            <div key={index} className="flex flex-col">
              {getDate(msgTime, prevTime)}
              {msg.senderId === userId ? (
                <UserMsgBox msg={message} />
              ) : (
                <BotMsgBox msg={message} />
              )}
            </div>
          );
        })}
      </div>

      <Form {...form}>
        <form
          onSubmit={form.handleSubmit((data)=>(void onSubmit(data)))}
          className="h-16 w-full max-w-2xl items-center flex space-x-2 px-4 fixed bottom-0 bg-black/10 shadow-sm backdrop-blur-sm"
        >
          <FormField
            control={form.control}
            name="message"
            render={({ field }) => (
              <FormItem className="w-full">
                <FormControl>
                  <Input {...field}  className="h-10" />
                </FormControl>
              </FormItem>
            )}
          />
          <Button type="submit" className="px-2 py-2 h-fit">
            <PaperPlaneIcon className="w-6 h-6" />
          </Button>
        </form>
      </Form>
    </div>
  );
};

// const chat = [
//   {
//     message: "Hi",
//     createAt: 1690439387000,
//     senderId: 0,
//   },
//   {
//     message: "Hello. How can I help You?",
//     createAt: 1690439387000,
//     senderId: 2,
//     feedback: {
//       isSent: true,
//       isDelivered: true,
//       isSeen: true,
//     },
//   },
//   {
//     message: "Can I get details of my last transaction I made last month? 🤔",
//     createAt: 1690439387000,
//     senderId: 0,
//     feedback: {
//       isSent: true,
//       isDelivered: true,
//       isSeen: true,
//     },
//   },
// ];
