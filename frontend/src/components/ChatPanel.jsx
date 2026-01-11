// frontend/src/components/ChatPanel.jsx
import { useState } from "react";
import { askStream } from "../api/ragApi";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function ChatPanel({ disabled }) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [citations, setCitations] = useState([]);
  const [loading, setLoading] = useState(false);

  const ask = async () => {
    if (disabled) return;

    setAnswer("");
    setCitations([]);
    setLoading(true);

    let buffer = "";

    try {
      await askStream(question, (chunk) => {
        buffer += chunk;

        if (buffer.includes("<<CITATIONS>>")) {
          const [text, citationJson] = buffer.split("<<CITATIONS>>");
          setAnswer(text.trim());

          try {
            const parsed = JSON.parse(citationJson);
            setCitations(parsed.citations || []);
          } catch {
            /* ignore */
          }
        } else {
          setAnswer(buffer);
        }
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <textarea
        className="border p-3 rounded-md"
        rows={3}
        placeholder={
          disabled
            ? "Ingestion in progress… please wait"
            : "Ask a technical question..."
        }
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        disabled={disabled}
      />

      <button
        onClick={ask}
        disabled={loading || disabled}
        className={`px-4 py-2 rounded-md text-white ${
          disabled ? "bg-gray-400" : "bg-freudenberg"
        }`}
      >
        {disabled ? "Ingesting…" : loading ? "Thinking…" : "Ask"}
      </button>

      <div className="bg-white p-4 rounded-md shadow prose prose-slate max-w-none">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {answer}
        </ReactMarkdown>
      </div>

      {citations.length > 0 && (
        <div className="bg-freudenberg-light p-4 rounded-md border border-freudenberg/20">
          <strong>Sources:</strong>
          <ul className="list-disc ml-5">
            {citations.map((c, i) => (
              <li key={i}>
                <a
                  href={`https://rag-technical-assistant-manuals.s3.us-east-1.amazonaws.com/manuals/${c.source}#page=${c.page_number}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 underline"
                >
                  {c.source}
                </a>
                , PDF Page {c.page_number}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
