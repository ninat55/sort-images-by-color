# sort-images-by-color

A web app for uploading images and sorting them by color. Designed for 1:1 aspect ratio images, displayed as 100×100px thumbnails.

## Requirements

```bash
pip install -r requirements.txt
```

## Running the app

### Backend

```bash
source env/bin/activate
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```
