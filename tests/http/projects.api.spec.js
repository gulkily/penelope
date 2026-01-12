const { test, expect } = require("@playwright/test");

test("project endpoints accept updates", async ({ request }) => {
  const name = `API Project ${Date.now()}`;
  const objective = `API Objective ${Date.now()}`;
  const progress = 42;

  const createResponse = await request.post("/api/projects", {
    data: { name },
  });
  expect(createResponse.ok()).toBeTruthy();
  const createPayload = await createResponse.json();
  const projectId = createPayload.project?.id;
  expect(projectId).toBeTruthy();

  const objectiveResponse = await request.put(
    `/api/projects/${projectId}/objective`,
    { data: { objective } }
  );
  expect(objectiveResponse.ok()).toBeTruthy();

  const progressResponse = await request.put(`/api/projects/${projectId}/progress`, {
    data: { progress },
  });
  expect(progressResponse.ok()).toBeTruthy();

  const projectResponse = await request.get(`/api/projects/${projectId}`);
  expect(projectResponse.ok()).toBeTruthy();
  const projectPayload = await projectResponse.json();
  expect(projectPayload.objective).toBe(objective);
  expect(projectPayload.progress).toBe(progress);
});
