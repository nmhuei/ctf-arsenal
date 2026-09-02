const state = {
  user: null,
  secrets: [],
  users: [],
  audit: [],
  editingSecret: null,
};
const $ = (id) => document.getElementById(id);
const api = async (url, options = {}) => {
  const response = await fetch(url, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok)
    throw new Error(
      body.error || "The corporate network declined this request.",
    );
  return body;
};
const notify = (message, error = false) => {
  const toast = $("toast");
  toast.textContent = message;
  toast.className = `toast show${error ? " error" : ""}`;
  setTimeout(() => (toast.className = "toast"), 3500);
};
const initials = (email) => (email || "B").slice(0, 1).toUpperCase();
const niceDate = (value) =>
  value
    ? new Date(
        value.replace(" ", "T") + (value.includes("Z") ? "" : "Z"),
      ).toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        year: "numeric",
      })
    : "—";
const actionLabel = (action) =>
  action.replaceAll("_", " ").replaceAll(".", " · ");

async function boot() {
  try {
    state.user = await api("/api/v1/me");
    showApp();
    await loadAll();
  } catch (_) {
    $("login-view").classList.remove("hidden");
  }
}
function showApp() {
  $("login-view").classList.add("hidden");
  $("app-view").classList.remove("hidden");
  $("user-email").textContent = state.user.email;
  $("user-avatar").textContent = initials(state.user.email);
  $("first-name").textContent = state.user.email
    .split("@")[0]
    .split(/[._-]/)[0];
  if (state.user.role !== "admin")
    document.querySelectorAll(".admin-only").forEach((el) => el.remove());
}
async function loadAll() {
  const secretData = await api("/api/v1/secrets");
  state.secrets = secretData.secrets;
  renderSecrets();
  $("metric-secrets").textContent = state.secrets.length
    .toString()
    .padStart(2, "0");
  if (state.user.role === "admin") {
    const [users, audit] = await Promise.all([
      api("/api/v1/users"),
      api("/api/v1/audit"),
    ]);
    state.users = users.users;
    state.audit = audit.events;
    $("metric-events").textContent = audit.events.length
      .toString()
      .padStart(2, "0");
    renderUsers();
    renderAudit();
  } else $("metric-events").textContent = "—";
}
function renderSecrets(filter = "") {
  const list = state.secrets.filter((s) =>
    `${s.name} ${s.description}`.toLowerCase().includes(filter.toLowerCase()),
  );
  $("secret-count").textContent =
    `${list.length} ASSET${list.length === 1 ? "" : "S"} · ENCRYPTED`;
  const empty =
    '<div class="empty-state">No secrets in this view. A rare moment of organizational clarity.</div>';
  $("recent-secrets").innerHTML =
    state.secrets.slice(0, 4).map(secretRow).join("") || empty;
  $("secrets-table").innerHTML =
    list
      .map(
        (s) =>
          `<tr><td><strong>${esc(s.name)}</strong><br><small class="muted">${esc(s.description || "No description")}</small></td><td>Owner #${s.owner_id}</td><td>${niceDate(s.updated_at)}</td><td><span class="access-pill">Authorized</span></td><td><button class="row-action reveal-action" data-id="${s.id}">Reveal ↗</button></td></tr>`,
      )
      .join("") || `<tr><td colspan="5">${empty}</td></tr>`;
  document
    .querySelectorAll(".reveal-action")
    .forEach(
      (button) => (button.onclick = () => revealSecret(button.dataset.id)),
    );
  document
    .querySelectorAll(".recent-card .row-action")
    .forEach(
      (button) => (button.onclick = () => revealSecret(button.dataset.id)),
    );
}
function secretRow(s) {
  return `<div class="secret-row"><span class="secret-glyph">◈</span><div class="secret-info"><strong>${esc(s.name)}</strong><small>${esc(s.description || "Protected asset")} · updated ${niceDate(s.updated_at)}</small></div><button class="row-action" data-id="${s.id}">Reveal ↗</button></div>`;
}
async function revealSecret(id) {
  try {
    const secret = await api(`/api/v1/secrets/${id}`);
    $("reveal-name").textContent = secret.name;
    $("revealed-value").textContent = secret.value;
    $("reveal-dialog").showModal();
  } catch (e) {
    notify(e.message, true);
  }
}
function renderUsers() {
  $("users-table").innerHTML = state.users
    .map(
      (u) =>
        `<tr><td><strong>${esc(u.email)}</strong><br><small class="muted">ID ${u.id}</small></td><td><span class="role-pill role-${u.role}">${u.role}</span></td><td><span class="access-pill">● Active</span></td><td>${niceDate(u.created_at)}</td></tr>`,
    )
    .join("");
}
function renderAudit() {
  $("audit-list").innerHTML =
    state.audit
      .map(
        (e) =>
          `<div class="audit-item"><span class="audit-icon">✓</span><div class="audit-info"><strong>${esc(actionLabel(e.action))}${e.secret_id ? ` <span class="muted">· secret #${e.secret_id}</span>` : ""}</strong><small>${niceDate(e.created_at)} · actor #${e.actor_id || "system"} · ${esc(e.ip || "internal")}</small></div></div>`,
      )
      .join("") ||
    '<p class="muted">No audit events yet. The auditors are getting restless.</p>';
}
function esc(value) {
  const node = document.createElement("span");
  node.textContent = value ?? "";
  return node.innerHTML;
}
function switchView(name) {
  document
    .querySelectorAll(".page-view")
    .forEach((v) => v.classList.add("hidden"));
  $(`${name}-view`).classList.remove("hidden");
  document
    .querySelectorAll(".nav-item")
    .forEach((b) => b.classList.toggle("active", b.dataset.view === name));
  $("page-label").textContent = name.toUpperCase().replace("-", " ");
}
function openSecretDialog() {
  $("secret-form").reset();
  $("secret-dialog").showModal();
}
async function exportVault() {
  try {
    const response = await fetch("/api/v1/vault/export", {
      credentials: "same-origin",
    });
    if (!response.ok) throw new Error("Vault export was rejected.");
    const blob = await response.blob();
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `vault-export-${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(link.href);
    notify("Vault export downloaded. Keep the source key separate.");
  } catch (e) {
    notify(e.message, true);
  }
}
async function importVault(event) {
  if (event.submitter?.value === "cancel") return;
  event.preventDefault();
  const file = $("import-file").files[0];
  if (!file) return notify("Choose a vault export first.", true);
  try {
    const exported = JSON.parse(await file.text());
    exported.key = $("import-key").value.trim();
    const result = await api("/api/v1/vault/import", {
      method: "POST",
      body: JSON.stringify(exported),
    });
    $("import-dialog").close();
    $("import-form").reset();
    notify(
      `${result.records} encrypted secret${result.records === 1 ? "" : "s"} imported.`,
    );
    await loadAll();
  } catch (e) {
    notify(e.message, true);
  }
}

$("login-form").onsubmit = async (event) => {
  event.preventDefault();
  const button = event.target.querySelector("button");
  button.disabled = true;
  try {
    const result = await api("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email: $("login-email").value,
        password: $("login-password").value,
      }),
    });
    state.user = result.user;
    showApp();
    await loadAll();
    notify("Authentication accepted. Welcome to the alignment layer.");
  } catch (e) {
    notify(e.message, true);
  } finally {
    button.disabled = false;
  }
};
$("logout-button").onclick = async () => {
  await api("/api/v1/auth/logout", { method: "POST" });
  location.reload();
};
document
  .querySelectorAll(".nav-item")
  .forEach(
    (button) => (button.onclick = () => switchView(button.dataset.view)),
  );
document
  .querySelectorAll("[data-view-link]")
  .forEach(
    (button) => (button.onclick = () => switchView(button.dataset.viewLink)),
  );
$("new-secret-button").onclick = openSecretDialog;
$("new-secret-button-2").onclick = openSecretDialog;
$("export-vault-button").onclick = exportVault;
if ($("import-vault-button"))
  $("import-vault-button").onclick = () => {
    $("import-form").reset();
    $("import-dialog").showModal();
  };
$("secret-form").onsubmit = async (event) => {
  if (event.submitter?.value === "cancel") return;
  event.preventDefault();
  try {
    await api("/api/v1/secrets", {
      method: "POST",
      body: JSON.stringify({
        name: $("secret-name").value,
        description: $("secret-description").value,
        value: $("secret-value").value,
      }),
    });
    $("secret-dialog").close();
    notify("Secret encrypted and committed to the vault.");
    await loadAll();
  } catch (e) {
    notify(e.message, true);
  }
};
$("import-form").onsubmit = importVault;
$("new-user-button").onclick = () => {
  $("user-form").reset();
  $("user-dialog").showModal();
};
$("user-form").onsubmit = async (event) => {
  if (event.submitter?.value === "cancel") return;
  event.preventDefault();
  try {
    await api("/api/v1/users", {
      method: "POST",
      body: JSON.stringify({
        email: $("new-user-email").value,
        password: $("new-user-password").value,
        role: $("new-user-role").value,
      }),
    });
    $("user-dialog").close();
    notify("Identity provisioned. Synergy permissions are pending review.");
    await loadAll();
  } catch (e) {
    notify(e.message, true);
  }
};
$("secret-search").oninput = (event) => renderSecrets(event.target.value);
$("copy-value").onclick = async () => {
  await navigator.clipboard.writeText($("revealed-value").textContent);
  notify("Copied. The clipboard has entered a need-to-know state.");
};
$("reseal-button").onclick = async () => {
  try {
    const result = await api("/api/v1/admin/vault/reseal", { method: "POST" });
    notify(`Vault resealed. ${result.records} records aligned.`);
    await loadAll();
  } catch (e) {
    notify(e.message, true);
  }
};
boot();
