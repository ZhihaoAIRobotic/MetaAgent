import { BotAvatar } from "@/components/chat/BotAvatar";
import { BotMsgBox } from "@/components/chat/BotMsgBox";
import { UserMsgBox } from "@/components/chat/UserMsgBox";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PaperPlaneIcon } from "@radix-ui/react-icons";
import { format, isSameDay } from "date-fns";
import { useForm, SubmitHandler } from "react-hook-form";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";

// temp data
const doamin = "https://u51443-9850-22580c53.neimeng.seetacloud.com:6443";
const userId = 0;
// curl --request POST 'https://u51443-9850-22580c53.neimeng.seetacloud.com:6443/chat' --header 'Content-Type: application/json' -d '{"data": [{"text": "hello world"}], "parameters": {"param1": "hello world"}}'

const FormSchema = z.object({
  message: z.string().min(1),
});

export const ChatContainer = () => {
  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
  });

  const onSubmit = (
    data: z.infer<typeof FormSchema>,
    e?: React.BaseSyntheticEvent,
  ) => {
    e?.preventDefault();
    // console.log(data);

    const { message } = data;
    fetchChat(message);
  };

  const fetchChat = async (msg: string) => {
    try {
      const res = await fetch(`${doamin}/chat`, {
        method: "Post",
        headers: {
          // "X-RapidAPI-Key": "your-api-key",
          // "X-RapidAPI-Host": "api.com",
          // 'Authorization': 'Basic ' + base64.encode("APIKEY:X"),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          data: [{ text: msg }],
        }),
      });
      const data = await res.json();
      console.log(data);
    } catch (err) {
      console.log(err);
    }
  };

  const getDate = (current: Date, previous?: Date) => {
    if (!previous || !isSameDay(current, previous)) {
      <div className="text-center text-gray-400 text-xs py-2">
        {format(current, "dd-MMMM-yyyy")}
      </div>;
    }

    return;
  };

  return (
    <div className="relative rounded-md shadow-lg w-full max-w-2xl h-screen bg-gray-400/20 overflow-y-scroll scrollbar scrollbar-thumb-gray-900 scrollbar-track-gray-100">
      {/* Avatar */}
      <div className="w-full h-60 sticky top-0 backdrop-blur-sm shadow-sm py-5">
        <BotAvatar />
      </div>

      {/* Message Container */}
      <div className="flex flex-col space-y-2 pt-5 pb-24 px-10 ">
        {chat.map((msg, index) => {
          const { message } = msg;
          const msgTime = new Date(msg.createAt);
          const prevTime = chat[(index = 1)]
            ? new Date(chat[index - 1]?.createAt)
            : undefined;
          return (
            <>
              {getDate(msgTime, prevTime)}
              {msg.senderId === userId ? (
                <UserMsgBox msg={message} />
              ) : (
                <BotMsgBox msg={message} />
              )}
            </>
          );
        })}
      </div>

      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="h-16 w-full max-w-2xl items-center flex space-x-2 px-4 fixed bottom-0 bg-black/10 shadow-sm backdrop-blur-sm"
        >
          <FormField
            control={form.control}
            name="message"
            render={({ field }) => (
              <FormItem className="w-full">
                <FormControl>
                  <Input placeholder="......" {...field} className="h-10" />
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

const chat = [
  {
    message: "Hi",
    createAt: 1690165666,
    senderId: 0,
  },
  {
    message: "Hello. How can I help You?",
    createAt: 1690165766,
    senderId: 2,
    feedback: {
      isSent: true,
      isDelivered: true,
      isSeen: true,
    },
  },
  {
    message: "Can I get details of my last transaction I made last month? 🤔",
    createAt: 1690165886,
    senderId: 0,
    feedback: {
      isSent: true,
      isDelivered: true,
      isSeen: true,
    },
  },
];
