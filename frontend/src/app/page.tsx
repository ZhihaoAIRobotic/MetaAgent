// import WebSocketChat from "@/components/chat"; 
import dynamic from "next/dynamic";
import "@/app/globals.css";


const DefaultChat = dynamic(() => import("@/components/chatbox"), { ssr: false });

export default function Home() {
  return (
    <div className="container">
     <DefaultChat/>
    </div>
  );
}
