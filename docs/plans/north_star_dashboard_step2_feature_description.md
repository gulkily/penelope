# North Star Dashboard - Step 2 Feature Description

Problem: Teams need a single, consistent view to review a project's North Star progress and capture updates (summary, challenges, opportunities, milestones, and open questions) in one place.

User stories:
- As a project lead, I want to select a project and see its North Star status so that I can assess progress quickly.
- As a contributor, I want to add summary, challenge, opportunity, and milestone items so that updates are captured as they arise.
- As a stakeholder, I want to view the progress percentage alongside key notes so that I can understand trajectory at a glance.
- As a team member, I want to record open questions or risks so that they are tracked and visible to others.

Core requirements:
- Provide a project selector that drives all displayed data.
- Display North Star progress with a percentage and a visual progress indicator.
- Present four sections: Summary, Challenges, Opportunities, and Milestones, each with an "add item" action.
- Include a questions area for free-form capture of open issues or clarifications.
- Use a FastAPI backend with a vanilla HTML/CSS/JS frontend (no React/Tailwind or third-party UI frameworks).

Shared component inventory:
- No existing UI or API surfaces in this repository yet; new components are required.
- New UI elements: project selector, progress bar, four section cards, and questions field.

Simple user flow:
1. Open the North Star dashboard.
2. Select a project from the dropdown.
3. Review the progress bar and current items in each section.
4. Add a new item to one of the sections as needed.
5. Capture open questions in the questions field.
6. Confirm updates are reflected for the selected project.

Success criteria:
- Selecting a project reliably updates the progress value and section content.
- Adding an item makes it visible in the relevant section for that project.
- Questions are saved and displayed for the selected project.
- The layout matches the provided screenshot structure and spacing expectations.
