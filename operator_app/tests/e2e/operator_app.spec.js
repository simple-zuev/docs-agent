import { test, expect } from "@playwright/test";

test("operator app loads and shows task list", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("Operator Shell")).toBeVisible();
  await expect(page.getByText("Task Intake / Queue")).toBeVisible();
  await expect(page.getByText("Task Details / Workspace")).toBeVisible();
});

test("operator app shows selected task details", async ({ page }) => {
  await page.goto("/");

  const taskButton = page.getByRole("button", {
    name: /Prepare diagram package for exchange overview/i,
  });

  await expect(taskButton).toBeVisible();
  await taskButton.click();

  await expect(page.getByText("exchange_architecture.drawio")).toBeVisible();
});

test("operator app can create a task", async ({ page }) => {
  const title = `Playwright task ${Date.now()}`;

  await page.goto("/");
  await page.getByPlaceholder("Task title").fill(title);
  await page.getByRole("button", { name: "Create task" }).click();

  await expect(
    page.getByRole("button", {
      name: new RegExp(title.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")),
    }),
  ).toBeVisible();
});

test("operator app can update task state from created to in_progress", async ({ page }) => {
  const title = `State transition task ${Date.now()}`;

  await page.goto("/");
  await page.getByPlaceholder("Task title").fill(title);
  await page.getByRole("button", { name: "Create task" }).click();

  const createdTaskButton = page.getByRole("button", {
    name: new RegExp(title.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")),
  });

  await expect(createdTaskButton).toBeVisible();
  await createdTaskButton.click();

  await expect(page.getByRole("button", { name: "Start task" })).toBeVisible();
  await page.getByRole("button", { name: "Start task" }).click();

  const workspace = page.getByText("Task Details / Workspace").locator("..");
  await expect(workspace.getByText("in_progress")).toBeVisible();
});
