// import WebSocketChat from "@/components/chat"; 
import dynamic from "next/dynamic";
import "@/app/globals.css";
import Graph from "@/components/graphview"

const DefaultChat = dynamic(() => import("@/components/chatbox"), { ssr: false });

export default function Home() {
  return (
    <div>
     <Graph/>
    </div>
  );
}
