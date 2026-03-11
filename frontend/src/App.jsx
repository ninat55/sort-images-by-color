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

  function handleFile(event) {
    const file = event.target.files[0];
    setFile(file);
  }

  async function uploadFile() {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    await fetch(`${API_BASE}/upload-image`, {
      method: "POST",
      body: formData,
    });

    setFile(null);
    refresh();
  }

  async function saveUrl() {
    if (!url.trim()) return;

    await fetch(`${API_BASE}/save-url`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({url}),
    });

    setUrl('');
    refresh();
  }

  async function handleDelete(itemToDelete) {
    await fetch(`${API_BASE}/delete-image`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(itemToDelete),
    });

    refresh();
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
        {file && <p>Selected file: {file.name}</p>}
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
