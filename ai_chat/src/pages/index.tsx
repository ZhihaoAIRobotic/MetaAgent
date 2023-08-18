import { Inter } from "next/font/google";

import { ChatContainer } from "@/components/chat/ChatContainer";

const inter = Inter({ subsets: ["latin"] });

export default function form() {
  return (
    <main
      className={`flex min-h-screen justify-center space-y-10 ${inter.className}`}
    >
      <ChatContainer />
    </main>
  );
}
