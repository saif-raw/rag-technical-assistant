// frontend/src/pages/Home.jsx
import { useState } from "react";
import Header from "../components/Header";
import UploadPanel from "../components/UploadPanel";
import ChatPanel from "../components/ChatPanel";

export default function Home() {
  const [ingesting, setIngesting] = useState(false);

  return (
    <>
      <Header />
      <main className="max-w-4xl mx-auto p-6 grid gap-6">
        <UploadPanel
          onUploadStart={() => setIngesting(true)}
          onUploadEnd={() => setIngesting(false)}
        />
        <ChatPanel disabled={ingesting} />
      </main>
    </>
  );
}
