import React, { useEffect, useMemo, useState } from "react";
import Panel from "./components/Panel";
import { createTask, getTask, getTaskHistory, getTasks, updateTask } from "./api";

const packageFallback = {
  sourceArtifacts: ["source not loaded yet"],
  previewArtifacts: ["preview not loaded yet"],
  exportArtifacts: ["export package not loaded yet"],
  publicationTargets: ["publication target not loaded yet"],
  completeness: "mock_package_placeholder",
  warnings: ["Package review runtime is not connected yet."]
};

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [selectedTaskId, setSelectedTaskId] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);
  const [historyEvents, setHistoryEvents] = useState([]);
  const [isLoadingTasks, setIsLoadingTasks] = useState(true);
  const [isLoadingTaskDetails, setIsLoadingTaskDetails] = useState(false);
  const [createTitle, setCreateTitle] = useState("");
  const [createType, setCreateType] = useState("startup_check");
  const [error, setError] = useState("");

  async function loadTasks(preferredTaskId = null) {
    setIsLoadingTasks(true);
    setError("");
    try {
      const items = await getTasks();
      setTasks(items);
      const nextTaskId =
        preferredTaskId ?? selectedTaskId ?? (items.length > 0 ? items[0].task_id : null);
      setSelectedTaskId(nextTaskId);
    } catch (err) {
      setError(`Failed to load tasks: ${String(err.message || err)}`);
    } finally {
      setIsLoadingTasks(false);
    }
  }

  async function loadTaskDetails(taskId) {
    if (!taskId) {
      setSelectedTask(null);
      setHistoryEvents([]);
      return;
    }
    setIsLoadingTaskDetails(true);
    setError("");
    try {
      const [task, history] = await Promise.all([getTask(taskId), getTaskHistory(taskId)]);
      setSelectedTask(task);
      setHistoryEvents(history);
    } catch (err) {
      setError(`Failed to load task details: ${String(err.message || err)}`);
    } finally {
      setIsLoadingTaskDetails(false);
    }
  }

  useEffect(() => {
    loadTasks();
  }, []);

  useEffect(() => {
    loadTaskDetails(selectedTaskId);
  }, [selectedTaskId]);

  const nextActions = useMemo(() => {
    if (!selectedTask) return [];
    if (selectedTask.status === "awaiting_approval") {
      return [
        {
          label: "Mark approved",
          onClick: async () => {
            await handleUpdateTask({ approval_state: "approved", status: "in_progress" });
          }
        },
        {
          label: "Mark rejected",
          onClick: async () => {
            await handleUpdateTask({ approval_state: "rejected", status: "blocked" });
          }
        }
      ];
    }
    if (selectedTask.status === "created") {
      return [
        {
          label: "Start task",
          onClick: async () => {
            await handleUpdateTask({ status: "in_progress" });
          }
        }
      ];
    }
    if (selectedTask.status === "in_progress") {
      return [
        {
          label: "Await approval",
          onClick: async () => {
            await handleUpdateTask({
              status: "awaiting_approval",
              approval_state: "requested"
            });
          }
        },
        {
          label: "Complete task",
          onClick: async () => {
            await handleUpdateTask({ status: "completed" });
          }
        }
      ];
    }
    return [];
  }, [selectedTask]);

  async function handleCreateTask(event) {
    event.preventDefault();
    if (!createTitle.trim()) return;
    setError("");
    try {
      const created = await createTask({
        title: createTitle.trim(),
        task_type: createType
      });
      setCreateTitle("");
      await loadTasks(created.task_id);
    } catch (err) {
      setError(`Failed to create task: ${String(err.message || err)}`);
    }
  }

  async function handleUpdateTask(payload) {
    if (!selectedTaskId) return;
    setError("");
    try {
      await updateTask(selectedTaskId, payload);
      await loadTasks(selectedTaskId);
      await loadTaskDetails(selectedTaskId);
    } catch (err) {
      setError(`Failed to update task: ${String(err.message || err)}`);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <div className="eyebrow">docs-agent</div>
          <h1>Operator Shell</h1>
        </div>
        <div className="topbar-badge">connected to local backend task API</div>
      </header>

      {error ? <div className="error-banner">{error}</div> : null}

      <div className="layout">
        <aside className="left-column">
          <Panel title="Task Intake / Queue">
            <form className="create-task-form" onSubmit={handleCreateTask}>
              <input
                className="text-input"
                placeholder="Task title"
                value={createTitle}
                onChange={(event) => setCreateTitle(event.target.value)}
              />
              <select
                className="text-input"
                value={createType}
                onChange={(event) => setCreateType(event.target.value)}
              >
                <option value="startup_check">startup_check</option>
                <option value="find_document">find_document</option>
                <option value="read_document">read_document</option>
                <option value="inspect_artifact">inspect_artifact</option>
                <option value="prepare_doc_body">prepare_doc_body</option>
                <option value="prepare_diagram_package">prepare_diagram_package</option>
                <option value="publish_to_slides">publish_to_slides</option>
              </select>
              <button className="primary-btn" type="submit">
                Create task
              </button>
            </form>

            <div className="section-meta">
              {isLoadingTasks ? "Loading tasks..." : `${tasks.length} task(s)`}
            </div>

            <div className="task-list">
              {tasks.map((task) => (
                <button
                  key={task.task_id}
                  className={`task-card ${task.task_id === selectedTaskId ? "active" : ""}`}
                  onClick={() => setSelectedTaskId(task.task_id)}
                >
                  <div className="task-card-title">{task.title}</div>
                  <div className="task-card-meta">
                    <span>{task.task_type}</span>
                    <span>{task.status}</span>
                  </div>
                </button>
              ))}
            </div>
          </Panel>

          <Panel title="Task History / Audit">
            <div className="section-meta">
              {isLoadingTaskDetails ? "Loading history..." : `${historyEvents.length} event(s)`}
            </div>
            <div className="history-list">
              {historyEvents.map((event) => (
                <div key={event.event_id} className="history-item">
                  <div className="history-top">
                    <span>{event.timestamp}</span>
                    <span>{event.event_type}</span>
                  </div>
                  <div className="history-summary">{event.summary}</div>
                  <div className="history-meta">{event.result_state}</div>
                </div>
              ))}
            </div>
          </Panel>
        </aside>

        <main className="center-column">
          <Panel title="Task Details / Workspace">
            {!selectedTask ? (
              <div className="empty-state">No task selected.</div>
            ) : (
              <>
                <div className="workspace-grid">
                  <div className="info-block">
                    <div className="label">Task</div>
                    <div className="value strong">{selectedTask.title}</div>
                  </div>
                  <div className="info-block">
                    <div className="label">Type</div>
                    <div className="value">{selectedTask.task_type}</div>
                  </div>
                  <div className="info-block">
                    <div className="label">Status</div>
                    <div className="value">{selectedTask.status}</div>
                  </div>
                  <div className="info-block">
                    <div className="label">Output state</div>
                    <div className="value">{selectedTask.output_state}</div>
                  </div>
                  <div className="info-block">
                    <div className="label">Drive object</div>
                    <div className="value">{selectedTask.drive_object_title}</div>
                  </div>
                  <div className="info-block">
                    <div className="label">Object role</div>
                    <div className="value">{selectedTask.object_role}</div>
                  </div>
                  <div className="info-block">
                    <div className="label">Placement state</div>
                    <div className="value">{selectedTask.placement_state}</div>
                  </div>
                  <div className="info-block">
                    <div className="label">Safe for mutation</div>
                    <div className="value">{String(selectedTask.safe_for_mutation)}</div>
                  </div>
                </div>

                <div className="action-rail">
                  {nextActions.map((action) => (
                    <button
                      key={action.label}
                      className="secondary-btn"
                      onClick={action.onClick}
                    >
                      {action.label}
                    </button>
                  ))}
                </div>
              </>
            )}
          </Panel>

          <Panel title="Artifact / Package Review">
            <div className="package-columns">
              <div>
                <div className="subhead">Source</div>
                <ul>
                  {packageFallback.sourceArtifacts.map((x) => (
                    <li key={x}>{x}</li>
                  ))}
                </ul>
              </div>
              <div>
                <div className="subhead">Preview</div>
                <ul>
                  {packageFallback.previewArtifacts.map((x) => (
                    <li key={x}>{x}</li>
                  ))}
                </ul>
              </div>
              <div>
                <div className="subhead">Exports</div>
                <ul>
                  {packageFallback.exportArtifacts.map((x) => (
                    <li key={x}>{x}</li>
                  ))}
                </ul>
              </div>
              <div>
                <div className="subhead">Publication</div>
                <ul>
                  {packageFallback.publicationTargets.map((x) => (
                    <li key={x}>{x}</li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="package-status">
              <div>
                <span className="label">Package state:</span> {packageFallback.completeness}
              </div>
              <div className="warning-box">
                {packageFallback.warnings.map((warning) => (
                  <div key={warning}>{warning}</div>
                ))}
              </div>
            </div>
          </Panel>
        </main>

        <aside className="right-column">
          <Panel title="Instruction Panel" tone="authority">
            {!selectedTask ? (
              <div className="empty-state">No authority context loaded.</div>
            ) : (
              <div className="stack">
                <div>
                  <span className="label">Authoritative source:</span> {selectedTask.authority_source}
                </div>
                <div>
                  <span className="label">Topic:</span> {selectedTask.authority_topic}
                </div>
                <div>
                  <span className="label">Relevant section:</span> {selectedTask.relevant_section}
                </div>
                <div className="hint-box">{selectedTask.operator_hint}</div>
              </div>
            )}
          </Panel>

          <Panel title="Approval Panel" tone="risk">
            {!selectedTask ? (
              <div className="empty-state">No approval state loaded.</div>
            ) : (
              <div className="stack">
                <div>
                  <span className="label">Approval state:</span> {selectedTask.approval_state}
                </div>
                <div>
                  <span className="label">Task status:</span> {selectedTask.status}
                </div>
                <div className="hint-box">
                  Approval-sensitive actions stay explicit and operator-visible.
                </div>
                <div className="button-row">
                  <button
                    className="secondary-btn"
                    onClick={() =>
                      handleUpdateTask({
                        approval_state: "approved",
                        status: "in_progress"
                      })
                    }
                  >
                    Approve
                  </button>
                  <button
                    className="secondary-btn"
                    onClick={() =>
                      handleUpdateTask({
                        approval_state: "rejected",
                        status: "blocked"
                      })
                    }
                  >
                    Reject
                  </button>
                </div>
              </div>
            )}
          </Panel>
        </aside>
      </div>
    </div>
  );
}
