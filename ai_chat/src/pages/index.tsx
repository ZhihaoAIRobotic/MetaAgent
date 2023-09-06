import { Inter } from "next/font/google";
import Link from "next/link";

import { ChatContainer } from "@/components/chat/ChatContainer";
import { BotIcon } from "@/images/Bot";
import { Chat } from "@/images/Chat";

const inter = Inter({ subsets: ["latin"] });

export default function form() {
  return (
    <div className="bg-[#27272A]">
      <div className="fixed left-10 top-4 flex h-fit flex-col gap-4 rounded-full bg-gray-100/80 p-2">
        <Link href={"/"} className="rounded-full p-2 hover:bg-gray-500/50">
          <Chat />
        </Link>
        <Link href={"/bot"} className="rounded-full p-2 hover:bg-gray-500/50">
          <BotIcon />
        </Link>
      </div>
      <main
        className={`flex min-h-screen justify-center space-y-10 ${inter.className}`}
      >
        <ChatContainer />
      </main>
    </div>
  );
}
