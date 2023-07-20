import { Inter } from "next/font/google";
import { ChatContainer } from "@/components/chat/ChatContainer";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@radix-ui/react-checkbox";

const inter = Inter({ subsets: ["latin"] });

export default function form() {
  return (
    <main
      className={`flex min-h-screen space-y-10 justify-center ${inter.className}`}
    >
      <ChatContainer />
    </main>
  );
}
