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
    if (disabled || !question.trim()) return;

    setAnswer("");
    setCitations([]);
    setLoading(true);

    let buffer = "";

    try {
      await askStream(question, (chunk) => {
        buffer += chunk;

        // Split streamed content and citations
        if (buffer.includes("<<CITATIONS>>")) {
          const [text, citationJson] = buffer.split("<<CITATIONS>>");
          setAnswer(text.trim());

          try {
            const parsed = JSON.parse(citationJson);
            setCitations(parsed.citations || []);
          } catch {
            // ignore malformed partial JSON during stream
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
        className="border p-3 rounded-md focus:ring-2 focus:ring-freudenberg outline-none"
        rows={3}
        placeholder={
          disabled
            ? "Ingestion in progress… please wait"
            : "Ask a technical question (e.g., 'Show me the diagram for the heat exchanger')..."
        }
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        disabled={disabled}
      />

      <button
        onClick={ask}
        disabled={loading || disabled || !question.trim()}
        className={`px-4 py-2 rounded-md text-white font-semibold transition-colors ${
          disabled || loading ? "bg-gray-400" : "bg-freudenberg hover:bg-opacity-90"
        }`}
      >
        {disabled ? "Ingesting…" : loading ? "Thinking…" : "Ask Technical Oracle"}
      </button>

      {/* ANSWER AREA */}
      {answer && (
        <div className="bg-white p-6 rounded-md shadow-md prose prose-slate max-w-none border-t-4 border-freudenberg">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              // This is the LinkRenderer logic integrated directly
              a: ({ href, children }) => (
                <a
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 font-medium underline decoration-blue-400 hover:decoration-blue-600 transition-all"
                  title="Open source manual in new tab"
                >
                  {children}
                </a>
              ),
            }}
          >
            {answer}
          </ReactMarkdown>
        </div>
      )}

      {/* SOURCES AREA */}
      {citations.length > 0 && (
        <div className="bg-gray-50 p-4 rounded-md border border-gray-200">
          <div className="flex items-center gap-2 mb-2 text-gray-700">
            <span className="font-bold text-sm uppercase tracking-wider">Verified Sources</span>
          </div>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {citations.map((c, i) => (
              <li key={i} className="text-sm flex items-start gap-2 bg-white p-2 rounded border border-gray-100 shadow-sm">
                <span className="bg-gray-200 text-gray-700 px-1.5 py-0.5 rounded text-xs font-mono">
                  PG {c.page}
                </span>
                <a
                  href={c.url} // This is the S3 Presigned URL from the backend
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 underline truncate"
                >
                  {c.file_name}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}