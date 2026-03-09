# sort-images-by-color

A web app for uploading images and sorting them by color.

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

## Planned improvements

- add UUIDs to avoid image overwrites
- support multiple uploads
- improve color analysis
  - ignore low-saturation pixels
  - crop center region
  - resize and blur before analysis