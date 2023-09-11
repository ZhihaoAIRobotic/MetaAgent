import type { AppProps } from "next/app";
import { Inter } from "next/font/google";
import Link from "next/link";
import { NextPage } from "next/types";
import { ReactElement, ReactNode } from "react";

import { BotIcon } from "@/images/Bot";
import { Chat } from "@/images/Chat";
import "@/styles/globals.css";

export type NextPageWithLayout<P = object, IP = P> = NextPage<P, IP> & {
  getLayout?: (page: ReactElement, route?: string) => ReactNode;
};

type AppPropsWithLayout = AppProps & {
  Component: NextPageWithLayout;
};

const inter = Inter({ subsets: ["latin"] });

export default function App({ Component, pageProps }: AppPropsWithLayout) {
  const getLayout =
    Component.getLayout ?? ((page) => <AppLayout>{page}</AppLayout>);

  return getLayout(<Component {...pageProps} />);
}

const AppLayout = ({ children }: { children: React.ReactNode }) => {
  return (
    <main
      className={`bg-[#27272A] ${inter.className} h-screen w-full gap-4 p-4 md:flex`}
    >
      <div className="fixed z-10 h-fit w-fit flex-col gap-4 rounded-md bg-gray-50/10 p-2 text-white md:relative md:flex">
        <Link
          href={"/"}
          className="flex items-center gap-2 rounded-sm p-2 hover:bg-gray-500/20"
        >
          <Chat /> Chat
        </Link>
        <Link
          href={"/bot"}
          className="flex items-center gap-2 rounded-sm p-2 hover:bg-gray-500/20"
        >
          <BotIcon /> Bot
        </Link>
      </div>

      {children}
    </main>
  );
};
