const API_BASE = "/api";

async function parseJson(response) {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `HTTP ${response.status}`);
  }
  return response.json();
}

export async function getTasks() {
  return parseJson(await fetch(`${API_BASE}/tasks`));
}

export async function getTask(taskId) {
  return parseJson(await fetch(`${API_BASE}/tasks/${taskId}`));
}

export async function getTaskHistory(taskId) {
  return parseJson(await fetch(`${API_BASE}/tasks/${taskId}/history`));
}

export async function createTask(payload) {
  return parseJson(
    await fetch(`${API_BASE}/tasks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
  );
}

export async function updateTask(taskId, payload) {
  return parseJson(
    await fetch(`${API_BASE}/tasks/${taskId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
  );
}
