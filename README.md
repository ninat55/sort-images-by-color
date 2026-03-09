# sort-images-by-color

A web app for uploading images and sorting them by color.

## Requirements

```bash
pip install -r requirements.txt
```

## Running the App

### Backend

source env/bin/activate
uvicorn main:app --reload

### Frontend

cd frontend
npm install
npm run dev

## Planned Improvements

- add UUIDs to avoid image overwrites
- support multiple uploads
- improve color analysis
  - ignore low-saturation pixels
  - crop center region
  - resize and blur before analysis