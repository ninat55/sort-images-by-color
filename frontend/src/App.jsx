import { useState, useEffect } from 'react'
import './App.css'
import deleteIcon from './assets/delete-icon.svg'

const API_BASE = 'http://localhost:8000'

function App() {
  const [file, setFile] = useState(null);
  const [files, setFiles] = useState([]);
  const [url, setUrl] = useState('')
  const [toast, setToast] = useState("")

  async function refresh() {
    const res = await fetch(`${API_BASE}/uploads-list`);
    const data = await res.json();
    setFiles(data.files);
  }

  async function sort(filesToSort) {
    const res = await fetch(`${API_BASE}/sort`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(filesToSort),
    });

    const data = await res.json();
    setFiles(data.files);
  }

  function handleFile(event) {
    const file = event.target.files[0];
    setFile(file);
  }

  async function uploadFile() {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_BASE}/upload-image`, {
      method: "POST",
      body: formData,
    });

    const newItem = await res.json();

    setFile(null);
    const updatedFiles = [...files, newItem].sort((a, b) => a.angle - b.angle);
    setFiles(updatedFiles);
  }

  async function saveUrl() {
    if (!url.trim()) return;

    const res = await fetch(`${API_BASE}/save-url`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url }),
    });

    const newItem = await res.json();

    setUrl("");
    const updatedFiles = [...files, newItem].sort((a, b) => a.angle - b.angle);
    setFiles(updatedFiles);
  }

  async function handleDelete(itemToDelete) {
    const res = await fetch(`${API_BASE}/delete-image`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(itemToDelete),
    });

    if (!res.ok) return;

    const updatedFiles = files
      .filter(item =>
            !(item.type === itemToDelete.type &&
              item.src === itemToDelete.src))
      .sort((a, b) => a.angle - b.angle);
  
    setFiles(updatedFiles);
  }

  async function copyHtml() {  // check if needs refresh first
    const html = files
      .filter(item => item.type != "file")
      .map(item => `<img src="${item.src}" width="100"/>`)
      .join(" ");
    
    await navigator.clipboard.writeText(html)
    setToast("Copied!")

    setTimeout(() => {setToast("")}, 2000)
  }

  // refresh gallery upon initial load
  useEffect(() => {
    refresh();
  }, []);


  return (
  <div>
    <div className='uploads'>
      <div className='upload-image'>
        <input type="file" onChange={handleFile} />
        
        <button onClick={uploadFile}>Upload</button>
      </div>

      <div className="add-url">
        <input
          type="text"
          placeholder="Paste image URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button onClick={saveUrl}>Add URL</button>
      </div>
    </div>

    <div className="gallery">
      {files.map((item) =>
        (<div className="image-card"
             key={item.src}
             onClick={() => handleDelete(item)}>
          <img src={item.type == "file" ? `${API_BASE}/uploads/${encodeURIComponent(item.src)}`
                                        : item.src}
               width={100}/>
          <img className="delete-icon" src={deleteIcon} alt="Delete"/>
        </div>))}
    </div>

    <div className='copy-html'>
      <button onClick={copyHtml}>Copy HTML</button>
      {toast && <div className="toast">{toast}</div>}
    </div>
  </div>
);
}


export default App
