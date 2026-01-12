// frontend/src/api/ragApi.js
const API_BASE = "http://localhost:8000";

export async function uploadDocument(file, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append("file", file);

    xhr.open("POST", "http://localhost:8000/upload");

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    };

    xhr.onload = () => resolve(JSON.parse(xhr.responseText));
    xhr.onerror = reject;

    xhr.send(formData);
  });
}


export async function askStream(question, onToken) {
  const res = await fetch(`${API_BASE}/ask/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: question }),
  });

  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    onToken(decoder.decode(value));
  }
}

export async function ask(question) {
  const res = await fetch("http://localhost:8000/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: question }),
  });

  return res.json();
}
