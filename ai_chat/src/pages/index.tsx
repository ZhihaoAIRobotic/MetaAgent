import { Inter } from "next/font/google";
import Link from "next/link";

import { ChatContainer } from "@/components/chat/ChatContainer";
import { BotIcon } from "@/images/Bot";
import { Chat } from "@/images/Chat";

const inter = Inter({ subsets: ["latin"] });

export default function form() {
  return (
    <div className="h-screen w-full items-center justify-center gap-4 bg-[#27272A] md:flex md:pr-10">
      <div className="fixed left-10 top-4 z-10 flex h-fit w-fit flex-col gap-4 rounded-full bg-gray-50/10 p-2 md:relative md:left-0">
        <Link href={"/"} className="rounded-full p-2 hover:bg-gray-500/20">
          <Chat />
        </Link>
        <Link href={"/bot"} className="rounded-full p-2 hover:bg-gray-500/20">
          <BotIcon />
        </Link>
      </div>

      <main
        className={`flex h-screen w-full  max-w-2xl  items-center justify-center ${inter.className}`}
      >
        <ChatContainer />
      </main>
    </div>
  );
}
