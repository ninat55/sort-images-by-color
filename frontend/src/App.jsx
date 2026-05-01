import { useState, useEffect, useRef } from 'react'
import './App.css'

const API_BASE = 'http://localhost:8000'

function App() {
  const [file, setFile] = useState(null);
  const [files, setFiles] = useState([]);
  const [url, setUrl] = useState('')
  const [toast, setToast] = useState("")
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  async function refresh() {
    const res = await fetch(`${API_BASE}/uploads-list`);
    const data = await res.json();
    setFiles(data.files);
    setLoading(false);
  }

  function handleFile(event) {
    const f = event.target.files[0];
    setFile(f);
  }

  async function uploadFile() {
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_BASE}/upload-image`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      setUploading(false);
      showToast("Upload failed.");
      return;
    }

    const newItem = await res.json();

    setFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
    const updatedFiles = [...files, newItem].sort((a, b) => a.angle - b.angle);
    setFiles(updatedFiles);
    setUploading(false);
    showToast("Image uploaded!");
  }

  async function saveUrl() {
    if (!url.trim()) return;

    setUploading(true);
    const res = await fetch(`${API_BASE}/save-url`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });

    if (!res.ok) {
      setUploading(false);
      showToast("Failed to add URL.");
      return;
    }

    const newItem = await res.json();

    setUrl("");
    const updatedFiles = [...files, newItem].sort((a, b) => a.angle - b.angle);
    setFiles(updatedFiles);
    setUploading(false);
    showToast("Image added!");
  }

  async function handleDelete(itemToDelete) {
    const res = await fetch(`${API_BASE}/delete-image`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(itemToDelete),
    });

    if (!res.ok) return;

    const updatedFiles = files
      .filter(item => !(item.type === itemToDelete.type && item.src === itemToDelete.src))
      .sort((a, b) => a.angle - b.angle);

    setFiles(updatedFiles);
  }

  async function copyHtml() {
    const html = files
      .filter(item => item.type !== "file")
      .map(item => `<img src="${item.src}" width="100"/>`)
      .join(" ");

    await navigator.clipboard.writeText(html);
    showToast("Copied to clipboard!");
  }

  function showToast(msg) {
    setToast(msg);
    setTimeout(() => setToast(""), 2000);
  }

  useEffect(() => {
    (async () => { await refresh(); })();
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <h1>Sort by Color</h1>
        <p className="subtitle">Add images and they'll be arranged by hue!</p>
      </header>

      <main className="app-main">
        <section className="uploads-section">
          <div className="upload-card">
            <span className="upload-label">Upload a file</span>
            <div className="file-input-row">
              <label className="file-input-label">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFile}
                  className="hidden-file-input"
                />
                <span className="file-input-btn">Choose file</span>
                <span className="file-name">{file ? file.name : "No file chosen"}</span>
              </label>
              <button
                onClick={uploadFile}
                disabled={!file || uploading}
                className="action-btn"
              >
                {uploading ? "Uploading…" : "Upload"}
              </button>
            </div>
          </div>

          <div className="divider-or"><span>or</span></div>

          <div className="upload-card">
            <span className="upload-label">Add from URL</span>
            <div className="url-input-row">
              <input
                type="text"
                placeholder="https://example.com/image.jpg"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && saveUrl()}
                className="url-input"
              />
              <button
                onClick={saveUrl}
                disabled={!url.trim() || uploading}
                className="action-btn"
              >
                Add
              </button>
            </div>
          </div>
        </section>

        {loading ? (
          <div className="empty-state">
            <div className="spinner" />
            <p>Loading gallery…</p>
          </div>
        ) : files.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🌈</div>
            <p>No images yet. Upload one or paste a URL to get started.</p>
          </div>
        ) : (
          <div className="gallery-container">
            <div className="gallery-header">
              <span className="gallery-count">{files.length} image{files.length !== 1 ? "s" : ""}</span>
              <button className="copy-btn" onClick={copyHtml}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
                </svg>
                Copy HTML
              </button>
            </div>

            <div className="gallery">
              {files.map((item) => (
                <div
                  className="image-card"
                  key={item.type + ':' + item.src}
                >
                  <img
                    src={item.type === "file"
                      ? `${API_BASE}/uploads/${encodeURIComponent(item.src)}`
                      : item.src}
                    width={100}
                    alt=""
                  />
                  <button
                    className="delete-btn"
                    onClick={() => handleDelete(item)}
                    title="Remove image"
                    aria-label="Remove image"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}

export default App
