import "@/styles/globals.css";
import type { AppProps } from "next/app";
import Layout from "@/components/layout/Layout";
import { Geist, Geist_Mono } from "next/font/google";
import { ThemeProvider } from "next-themes";
import { ConfigProvider } from "antd";

import 'antd/dist/reset.css';


const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export default function App({ Component, pageProps }: AppProps) {
  return (
    <ThemeProvider attribute="class">
      <ConfigProvider>
        <div className={`${geistSans.variable} ${geistMono.variable}`}>
          <Layout>
            <Component {...pageProps} />
          </Layout>
        </div>
      </ConfigProvider>
    </ThemeProvider>
  );
}
