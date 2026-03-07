import os
import re
import time

import pytest
from playwright.sync_api import expect

from tests.e2e.data_factory import unique_project_name
from tests.e2e.helpers import create_resident, open_dashboard_project

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def open_add_update_dialog(page) -> None:
    trigger = page.get_by_role("button", name="Add update")
    expect(trigger).to_be_enabled()
    trigger.click()
    expect(page.locator("#transcript-dialog")).to_be_visible()


def test_transcript_draft_autosave_restore_clear_per_resident(page):
    project_a = create_resident(page, BASE_URL, unique_project_name())
    project_b = create_resident(page, BASE_URL, unique_project_name())

    open_dashboard_project(page, BASE_URL, project_a)
    open_add_update_dialog(page)

    draft_text = "Resident A draft transcript"
    transcript_input = page.locator("#transcript-input")
    transcript_input.fill(draft_text)
    page.wait_for_function(
        """
        ([projectId, expected]) => {
          return localStorage.getItem(`transcriptDraft:${projectId}`) === expected;
        }
        """,
        arg=[project_a, draft_text],
    )

    page.locator("#transcript-close").click()
    open_add_update_dialog(page)
    expect(page.locator("#transcript-input")).to_have_value(draft_text)
    expect(page.locator("#transcript-status")).to_have_text("Draft restored.")

    page.locator("#transcript-clear").click()
    expect(page.locator("#transcript-input")).to_have_value("")
    page.wait_for_function(
        "(projectId) => localStorage.getItem(`transcriptDraft:${projectId}`) === null",
        arg=project_a,
    )

    open_dashboard_project(page, BASE_URL, project_b)
    open_add_update_dialog(page)
    expect(page.locator("#transcript-input")).to_have_value("")
    page.wait_for_function(
        "(projectId) => localStorage.getItem(`transcriptDraft:${projectId}`) === null",
        arg=project_b,
    )


def test_analyze_and_apply_transcript_updates_with_regeneration(page):
    project_id = create_resident(page, BASE_URL, unique_project_name())
    open_dashboard_project(page, BASE_URL, project_id)

    page.evaluate(
        """
        () => {
          window.__e2e_confetti_calls = 0;
          window.NorthStarConfetti = {
            triggerConfetti() {
              window.__e2e_confetti_calls += 1;
            }
          };
        }
        """
    )

    page.route(
        f"**/api/projects/{project_id}/transcript",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=(
                '{"proposal":{"summary":"Summary from transcript",'
                '"objective":"Transcript objective",'
                '"goal":120,'
                '"progress":25,'
                '"items_to_add":[{"section":"challenges","text":"New challenge from transcript"}]}}'
            ),
        ),
    )
    page.route(
        f"**/api/projects/{project_id}/questions/regenerate",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"job_id":"job-e2e","status":"queued"}',
        ),
    )

    poll_count = {"value": 0}

    def handle_regen_status(route):
        poll_count["value"] += 1
        if poll_count["value"] == 1:
            body = '{"job_id":"job-e2e","status":"running"}'
        else:
            body = (
                '{"job_id":"job-e2e","status":"completed",'
                '"questions":"Regenerated questions",'
                '"error":null}'
            )
        route.fulfill(status=200, content_type="application/json", body=body)

    page.route(
        f"**/api/projects/{project_id}/questions/regeneration/job-e2e",
        handle_regen_status,
    )

    open_add_update_dialog(page)
    page.locator("#transcript-input").fill("Mentor/mentee transcript text.")
    page.locator("#transcript-analyze").click()

    suggestions = page.locator("#transcript-suggestion-list .transcript-suggestion")
    expect(suggestions.first).to_be_visible()
    assert suggestions.count() >= 4
    suggestion_fields = page.evaluate(
        """
        () => Array.from(
          document.querySelectorAll("#transcript-suggestion-list .transcript-suggestion")
        ).map((entry) => entry.dataset.field)
        """
    )
    for field in ("objective", "goal", "progress", "item"):
        assert field in suggestion_fields
    expect(page.locator("#transcript-status")).to_have_text(
        "Review the suggested updates below."
    )

    page.locator("#transcript-apply").click()
    expect(page.locator("#transcript-dialog")).to_be_hidden()

    expect(page.locator("#objective-input")).to_have_value("Transcript objective")
    expect(page.locator("#goal-input")).to_have_value("120")
    expect(page.locator("#progress-percent")).to_have_text(re.compile(r"30\s*/\s*120"))
    expect(
        page.locator(
            ".section-list[data-section='challenges'] .section-item",
            has_text="New challenge from transcript",
        ).first
    ).to_be_visible()
    expect(page.locator("#questions-status")).to_have_text("Questions refreshed.")
    confetti_calls = page.evaluate("() => window.__e2e_confetti_calls || 0")
    assert confetti_calls >= 1


def test_transcript_analyze_error_and_offline_states(page):
    project_id = create_resident(page, BASE_URL, unique_project_name())
    open_dashboard_project(page, BASE_URL, project_id)

    page.route(
        f"**/api/projects/{project_id}/transcript",
        lambda route: route.fulfill(
            status=502,
            content_type="application/json",
            body='{"detail":"LLM unavailable"}',
        ),
    )

    open_add_update_dialog(page)
    page.locator("#transcript-input").fill("Transcript that will fail.")
    page.locator("#transcript-analyze").click()
    expect(page.locator("#transcript-status")).to_have_text(
        "Transcript analysis failed. Try again."
    )

    page.evaluate(
        """
        () => {
          try {
            Object.defineProperty(window.navigator, "onLine", {
              configurable: true,
              get: () => false,
            });
          } catch (_error) {}
          window.dispatchEvent(new Event("offline"));
        }
        """
    )
    offline_supported = page.evaluate("() => navigator.onLine === false")
    if not offline_supported:
        pytest.skip("Unable to simulate offline mode in this browser context.")

    page.locator("#transcript-analyze").click()
    expect(page.locator("#transcript-status")).to_have_text(
        "You're offline. We'll keep your transcript so you can retry when connected."
    )


def test_transcript_analyze_timeout_state(page):
    page.add_init_script(
        """
        (() => {
          const originalSetTimeout = window.setTimeout.bind(window);
          window.setTimeout = (handler, timeout, ...args) => {
            if (timeout === 45000) {
              return originalSetTimeout(handler, 50, ...args);
            }
            return originalSetTimeout(handler, timeout, ...args);
          };
        })();
        """
    )

    project_id = create_resident(page, BASE_URL, unique_project_name())
    open_dashboard_project(page, BASE_URL, project_id)

    def delayed_transcript(route):
        time.sleep(0.2)
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"proposal":{"objective":"Should timeout before this arrives"}}',
        )

    page.route(f"**/api/projects/{project_id}/transcript", delayed_transcript)

    open_add_update_dialog(page)
    page.locator("#transcript-input").fill("Transcript timeout check")
    page.locator("#transcript-analyze").click()
    expect(page.locator("#transcript-status")).to_have_text(
        "Analysis timed out on a slow connection. Try again when ready."
    )


def test_questions_regeneration_error_status_after_apply(page):
    project_id = create_resident(page, BASE_URL, unique_project_name())
    open_dashboard_project(page, BASE_URL, project_id)

    page.route(
        f"**/api/projects/{project_id}/transcript",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"proposal":{"objective":"Objective for regen error"}}',
        ),
    )
    page.route(
        f"**/api/projects/{project_id}/questions/regenerate",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"job_id":"job-error","status":"queued"}',
        ),
    )
    page.route(
        f"**/api/projects/{project_id}/questions/regeneration/job-error",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"job_id":"job-error","status":"error","error":"mock regeneration failure"}',
        ),
    )

    open_add_update_dialog(page)
    page.locator("#transcript-input").fill("Transcript for regeneration error state.")
    page.locator("#transcript-analyze").click()
    expect(page.locator("#transcript-apply")).to_be_enabled()
    page.locator("#transcript-apply").click()
    expect(page.locator("#transcript-dialog")).to_be_hidden()
    expect(page.locator("#questions-status")).to_have_text(
        "Questions refresh failed: mock regeneration failure"
    )
