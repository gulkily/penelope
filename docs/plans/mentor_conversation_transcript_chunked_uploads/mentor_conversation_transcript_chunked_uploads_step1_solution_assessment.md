# Mentor Transcript Chunked Uploads (Step 1: Solution Assessment)

## Problem statement
Audio uploads for transcription are single-request and fragile on slow or unstable connections, leading to failed uploads and lost time for mentors.

## Option A: Client-side chunking + backend reassembly
**Incremental path**
- Establishes a resumable upload session that the current `/api/transcriptions` flow can consume after reassembly.

**Pros**
- Resumable uploads without adding external storage.
- Works with the existing backend stack and API keys.
- Allows precise retry of failed chunks on low bandwidth.

**Cons**
- Requires new backend endpoints and temporary storage.
- Needs cleanup logic for abandoned uploads.
- More complex validation and error handling.

## Option B: Direct-to-storage multipart uploads
**Incremental path**
- Builds on Option A by offloading chunk storage to object storage and using the backend only for signing and finalization.

**Pros**
- Scales better for large files and many concurrent uploads.
- Resumable uploads are handled by the storage provider.
- Reduces backend bandwidth and memory pressure.

**Cons**
- Requires storage infrastructure and signed URL workflows.
- More moving parts for security and retention.
- Harder to support offline dev without mocks.

## Option C: Standard resumable upload protocol (e.g., tus)
**Incremental path**
- Builds on Option A by adopting a standard protocol and client library for resumable uploads.

**Pros**
- Battle-tested resumable upload behavior with existing clients.
- Clear spec for pause/resume across browsers.
- Reduces bespoke client logic.

**Cons**
- Adds a new dependency and protocol surface area.
- Requires server support or a dedicated upload service.
- Integration effort to bridge uploads to the transcription endpoint.

## Recommendation
Proceed with Option A if we want the fastest path to resumable uploads without new infrastructure. Choose Option B if we expect large files at scale, and Option C if we want a standards-based resumable protocol for long-term maintainability.
