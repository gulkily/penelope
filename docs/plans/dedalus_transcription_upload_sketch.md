# Dedalus Transcription Upload Flow (Sketch)

## Goal
Capture audio in the browser, upload it to the backend, and forward it to Dedalus
for transcription so the app can return text to the UI.

## High-level flow
1. Browser records audio (MediaRecorder) and produces a Blob.
2. Browser POSTs the Blob to the backend via `multipart/form-data`.
3. Backend forwards the file to Dedalus `/v1/audio/transcriptions` with the API key.
4. Backend returns the transcript text (and optional metadata) to the browser.

## Browser sketch (JS)
```javascript
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
const recorder = new MediaRecorder(stream);
const chunks = [];

recorder.ondataavailable = (event) => {
  if (event.data.size > 0) chunks.push(event.data);
};

recorder.onstop = async () => {
  const blob = new Blob(chunks, { type: recorder.mimeType || "audio/webm" });
  const formData = new FormData();
  formData.append("file", blob, "recording.webm");
  formData.append("model", "openai/whisper-1");
  formData.append("response_format", "json");

  const response = await fetch("/api/transcriptions", {
    method: "POST",
    body: formData,
  });
  const data = await response.json();
  console.log(data.text);
};

recorder.start();
// ...later...
recorder.stop();
```

## Backend sketch (FastAPI)
```python
from fastapi import APIRouter, File, UploadFile
import httpx
import os

router = APIRouter()

@router.post("/transcriptions")
async def transcribe_audio(file: UploadFile = File(...)):
    api_key = os.getenv("DEDALUS_API_KEY", "")
    headers = {"Authorization": f"Bearer {api_key}"}
    form = {
        "model": "openai/whisper-1",
        "response_format": "json",
    }
    files = {"file": (file.filename, await file.read(), file.content_type)}

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.dedaluslabs.ai/v1/audio/transcriptions",
            data=form,
            files=files,
            headers=headers,
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()
```

## Notes
- The browser should request mic permission and handle errors gracefully.
- For long recordings, chunked uploads or a pre-signed storage flow may be needed.
- This flow keeps the Dedalus API key server-side.
- Dedalus transcription currently supports OpenAI-prefixed `openai/whisper-1` only, so we use that model for compatibility.
- Single-mic, turn-taking audio should transcribe well, but speaker labeling will be best-effort.
- If speaker labels are desired in v1, consider a lightweight heuristic (e.g., prepend
  "Speaker A"/"Speaker B" when the transcript includes explicit cues) and treat true
  diarization as a future enhancement when multi-mic audio is available.
