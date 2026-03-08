import { useState, useEffect } from 'react'
import './App.css'

const API_BASE = 'http://localhost:8000'

function App() {
  const [file, setFile] = useState(null);
  const [files, setFiles] = useState([]);

  
  // helper functions

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

    await fetch(`${API_BASE}/upload`, {
      method: "POST",
      body: formData,
    });

    // also refresh gallery
    refresh();
  }


  // refresh gallery upon initial load
  useEffect(() => {
    refresh();
  }, []);


  return (
  <div>
    <div className='upload'>
      {/* User selects a file */}
      <input type="file" onChange={handleFile} />

      {/* Show filename ONLY if file exists */}
      {file && <p>Selected file: {file.name}</p>}

      {/* User clicks to upload */}
      <button onClick={uploadFile}>Upload</button>
    </div>

    {/* Always show gallery */}
    <div className='gallery'>
      {files.map(name => 
                (<img key={name} src={`${API_BASE}/uploads/${encodeURIComponent(name)}`} width={100}/> ))}
    </div>
  </div>
);
}


export default App
