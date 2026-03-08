# Documentation Index

This directory contains implementation guides, test references, planning artifacts, and research notes for the project.

## Start Here

- [Feature Development Process](../FEATURE_DEVELOPMENT_PROCESS.md): Canonical Step 1-4 workflow and approval/commit rules.
- [Production Install](production_install.md): Single-host deployment setup using SQLite.
- [Staging E2E Setup](staging_e2e_setup.md): How to run and validate staging-safe end-to-end checks.
- [Test Matrix](test_matrix.md): Coverage map of core product flows.

## Planning

- [Plans Index](plans/README.md): Entry point for feature planning artifacts and loose plan notes in `docs/plans/`.
- [Feature Process Prompts](feature_process/): Step-specific prompt templates used during planning.
  - [Step 1: Solution Assessment](feature_process/step1_solution_assessment.md)
  - [Step 2: Feature Description](feature_process/step2_feature_description.md)
  - [Step 3: Development Plan](feature_process/step3_development_plan.md)
  - [Step 4: Implementation](feature_process/step4_implementation.md)

## Operations and Architecture

- [Domain Admin Brief](domain_admin_brief.md): DNS/TLS/CORS handoff notes for domain administrators.
- [PostgreSQL Migration Guide](postgres_migration.md): Migration path from SQLite to Postgres.
- [Concurrency Estimate](concurrency_estimate.md): Capacity assumptions and throughput guidance.
- [Transcript Processor Overview](transcript_processor.md): Processing model and behavior for transcript handling.

## Testing and Quality Notes

- [E2E Test Suite Update Checklist (2026-03-05)](e2e_test_suite_update_checklist_2026-03-05.md): Recent E2E maintenance checklist.
- [Test Suite Coverage Review (2026-02-27)](test_suite_coverage_review_2026-02-27.md): Gap review and recommendations.

## Research and Recommendations

- [In-Person Recording + Transcription Recommendations](recommendations_transcription_tools.md): Tooling recommendations and tradeoffs.

## Blog Posts

- [Chrome Audio Upload MIME-Type Debugging](blogs/chrome_audio_upload_mime_debugging_blog.md): Incident write-up and fix notes.
