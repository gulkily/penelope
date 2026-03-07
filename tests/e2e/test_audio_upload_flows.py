import os

from playwright.sync_api import expect

from tests.e2e.data_factory import unique_project_name
from tests.e2e.helpers import create_resident, open_dashboard_project

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def open_add_update_dialog(page) -> None:
    trigger = page.get_by_role("button", name="Add update")
    expect(trigger).to_be_enabled()
    trigger.click()
    expect(page.locator("#transcript-dialog")).to_be_visible()


def set_audio_file(page, name: str, data: bytes) -> None:
    page.locator("#transcript-file-input").set_input_files(
        {"name": name, "mimeType": "audio/wav", "buffer": data}
    )
    expect(page.locator("#upload-preview")).to_be_visible()


def test_small_audio_upload_uses_single_request_path(page):
    project_id = create_resident(page, BASE_URL, unique_project_name())
    open_dashboard_project(page, BASE_URL, project_id)

    upload_session_calls = {"value": 0}

    def reject_chunked_path(route):
        upload_session_calls["value"] += 1
        route.fulfill(status=500, body="unexpected chunked upload")

    page.route("**/api/transcriptions/uploads**", reject_chunked_path)
    page.route(
        "**/api/transcriptions",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"text":"Small upload transcript","status":"complete","progress":100}',
        ),
    )

    open_add_update_dialog(page)
    set_audio_file(page, "small.wav", b"small-audio-bytes")
    page.locator("#upload-submit").click()

    expect(page.locator("#upload-status")).to_have_text("Transcript ready.")
    expect(page.locator("#transcript-input")).to_have_value("Small upload transcript")
    assert upload_session_calls["value"] == 0


def test_large_audio_upload_uses_chunked_path(page):
    project_id = create_resident(page, BASE_URL, unique_project_name())
    open_dashboard_project(page, BASE_URL, project_id)

    calls = {"create": 0, "chunk": 0, "complete": 0}

    def handle_create(route):
        calls["create"] += 1
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"upload_id":"upload-e2e","chunk_size":1048576,"expires_at":"2099-01-01T00:00:00Z"}',
        )

    def handle_chunk(route):
        calls["chunk"] += 1
        route.fulfill(
            status=200,
            content_type="application/json",
            body=(
                '{"upload_id":"upload-e2e",'
                f'"status":"uploading","received_chunks":{calls["chunk"]},"total_chunks":6'
                "}"
            ),
        )

    def handle_complete(route):
        calls["complete"] += 1
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"text":"Chunked upload transcript","status":"complete","progress":100}',
        )

    page.route("**/api/transcriptions/uploads", handle_create)
    page.route("**/api/transcriptions/uploads/upload-e2e/chunks", handle_chunk)
    page.route("**/api/transcriptions/uploads/upload-e2e/complete", handle_complete)
    page.route(
        "**/api/transcriptions",
        lambda route: route.fulfill(status=500, body="single upload should not be used"),
    )

    open_add_update_dialog(page)
    large_blob = b"a" * (5 * 1024 * 1024 + 2048)
    set_audio_file(page, "large.wav", large_blob)
    page.locator("#upload-submit").click()

    expect(page.locator("#upload-status")).to_have_text("Transcript ready.")
    expect(page.locator("#transcript-input")).to_have_value("Chunked upload transcript")
    assert calls["create"] == 1
    assert calls["chunk"] >= 2
    assert calls["complete"] == 1


def test_audio_upload_failure_shows_error_message(page):
    project_id = create_resident(page, BASE_URL, unique_project_name())
    open_dashboard_project(page, BASE_URL, project_id)

    page.route(
        "**/api/transcriptions",
        lambda route: route.fulfill(
            status=502,
            content_type="application/json",
            body='{"detail":"Mock transcription failure"}',
        ),
    )

    open_add_update_dialog(page)
    set_audio_file(page, "bad.wav", b"bad-audio")
    page.locator("#upload-submit").click()
    expect(page.locator("#upload-status")).to_have_text(
        "Upload failed: Mock transcription failure"
    )
