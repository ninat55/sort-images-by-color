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

## Planned improvements

- improve performance!
  - save image angles - don't recompute
  - avoid full refresh apart from first load; instead, append/delete
- fix centering for last line
- add a delete-all (that requires confirmation)
- ? don't add invalid URLs (no http) to hosted_urls.txt
- check for duplicate URLs (and maybe images)
- add UUIDs to avoid image overwrites
- support multiple uploads at a time
- ? improve color analysis
  - ignore low-saturation pixels
  - crop center region
  - resize and blur before analysis