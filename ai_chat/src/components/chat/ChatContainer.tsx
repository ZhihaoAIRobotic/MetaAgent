import { zodResolver } from "@hookform/resolvers/zod";
import { PaperPlaneIcon } from "@radix-ui/react-icons";
import { useLocalStorage } from "@react-hooks-library/core";
import axios from "axios";
import { format, isSameDay } from "date-fns";
import { useMemo } from "react";
import { type SubmitHandler, useForm } from "react-hook-form";
import * as z from "zod";

import { BotAvatar } from "@/components/chat/BotAvatar";
import { BotMsgBox } from "@/components/chat/BotMsgBox";
import { UserMsgBox } from "@/components/chat/UserMsgBox";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormField, FormItem } from "@/components/ui/form";
import { Input } from "@/components/ui/input";

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
};
type ResponseChat = {
  text: string;
  blob?: string;
};
type Response = {
  data: ResponseChat[];
};
type ApiRes = {
  data: Response;
};

export const ChatContainer = () => {
  const [state, setValue] = useLocalStorage("chat", "");
  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      message: "",
    },
  });

  const chat = useMemo(() => {
    if (!state) return [];

    const chat = JSON.parse(state) as Chat[];
    return chat.filter((v) => !!v);
  }, [state]);

  const onSubmit: SubmitHandler<z.infer<typeof FormSchema>> = async (data) => {
    const { message } = data;
    const newChat = {
      message,
      createAt: Date.now(),
      senderId: userId,
    };

    const res = await fetchChat(message);
    const newChatList = [...chat, newChat, res];
    console.log("newChatList: ", newChatList);
    setValue(JSON.stringify(newChatList));
    return;
  };

  const fetchChat = async (msg: string) => {
    try {
      const apiRes = await axios
        .post(`${doamin}/chat`, {
          text: msg,
          parameters: "hello world",
        })
        .then((response) => {
          const { data } = response as ApiRes;
          const { data: chatRes } = data;
          const { text, blob } = chatRes[0];
          const newChat = {
            message: text,
            blob,
            createAt: Date.now(),
            senderId: 1,
          };
          console.log({ newChat });
          return newChat;
        })
        .catch((err) => {
          console.log("error: ", err);
        });
      return apiRes;
    } catch (err) {
      console.log(err);
    }
  };

  const getDate = (current: Date, previous?: Date) => {
    if (!previous || !isSameDay(current, previous)) {
      return (
        <div className="py-2 text-center text-xs text-gray-400">
          {format(current, "dd MMMM yyyy")}
        </div>
      );
    }

    return null;
  };

  return (
    <div className="relative h-screen w-full max-w-2xl overflow-y-scroll rounded-md bg-gray-400/20 shadow-lg scrollbar scrollbar-thin scrollbar-thumb-gray-400/50">
      {/* Avatar */}
      <div className="sticky top-0 h-60 w-full py-5 shadow-sm backdrop-blur-sm">
        <BotAvatar />
      </div>

      {/* Message Container */}
      <div className="space-y-4 px-10 pb-24 pt-5 ">
        {chat.map((msg, index) => {
          const { message } = msg;
          const msgTime = new Date(msg.createAt);
          const prevTime = chat[index - 1]
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
          onSubmit={form.handleSubmit((data) => void onSubmit(data))}
          className="fixed bottom-0 flex h-16 w-full max-w-2xl items-center space-x-2 bg-black/10 px-4 shadow-sm backdrop-blur-sm"
        >
          <FormField
            control={form.control}
            name="message"
            render={({ field }) => (
              <FormItem className="w-full">
                <FormControl>
                  <Input {...field} className="h-10" />
                </FormControl>
              </FormItem>
            )}
          />
          <Button type="submit" className="h-fit px-2 py-2">
            <PaperPlaneIcon className="h-6 w-6" />
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
