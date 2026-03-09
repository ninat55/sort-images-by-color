import { useState, useEffect } from 'react'
import './App.css'

const API_BASE = 'http://localhost:8000'

function App() {
  const [file, setFile] = useState(null);
  const [files, setFiles] = useState([]);
  const [url, setUrl] = useState('')

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


  // refresh gallery upon initial load
  useEffect(() => {
    refresh();
  }, []);


  return (
  <div>
    <div className='upload-image'>
      <input type="file" onChange={handleFile} />
      {file && <p>Selected file: {file.name}</p>}
      <button onClick={uploadFile}>Upload</button>
    </div>

    <div className="save-url">
      <input
        type="text"
        placeholder="Paste image URL"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />
      <button onClick={saveUrl}>Add URL</button>
    </div>

    <div className='gallery'>
      {files.map((item) => (<img key={item.src} 
                                 src={item.type == "file" ? `${API_BASE}/uploads/${encodeURIComponent(item.src)}`
                                                        : item.src}
                                 width={100}/>))}
    </div>
  </div>
);
}


export default App
