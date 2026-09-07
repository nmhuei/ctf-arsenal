let personaId;
let sessionToken = "";
let userName = "";

const authScreen = document.querySelector("#auth-screen");
const archive = document.querySelector("#archive");
const state = document.querySelector("#state");
const personaName = document.querySelector("#persona-name");
const connection = document.querySelector("#connection");
const sessionStatus = document.querySelector("#session-status");
const sessionId = document.querySelector("#session-id");
const message = document.querySelector("#message");
const chatButton = document.querySelector("#chat");
const thread = document.querySelector("#messages");
const userNameInput = document.querySelector("#user-name");
const userPassword = document.querySelector("#user-password");
const userState = document.querySelector("#user-state");

function sessionHeaders(headers = {}) {
  return sessionToken ? { ...headers, "x-soul-session": sessionToken } : headers;
}

function setUserSession(body) {
  sessionToken = body.session;
  userName = body.username;
  localStorage.setItem("no-hot-water-club-session", sessionToken);
  localStorage.setItem("no-hot-water-club-user", userName);
  userNameInput.value = userName;
  userPassword.value = "";
  userState.textContent = `Resident ${userName} verified.`;
  authScreen.classList.add("auth-complete");
}

async function accountRequest(path) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ username: userNameInput.value, password: userPassword.value })
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || "User request failed.");
  setUserSession(body);
}

document.querySelector("#create-account").addEventListener("click", async () => {
  userState.textContent = "Registering resident...";
  try {
    await accountRequest("/api/accounts");
  } catch (error) {
    userState.textContent = error.message;
  }
});

document.querySelector("#sign-in").addEventListener("click", async () => {
  userState.textContent = "Checking building access...";
  try {
    await accountRequest("/api/sessions");
  } catch (error) {
    userState.textContent = error.message;
  }
});

function addMessage(kind, text) {
  const article = document.createElement("article");
  article.className = `message ${kind}-message`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  const paragraph = document.createElement("p");
  paragraph.textContent = text;
  bubble.append(paragraph);
  if (kind === "assistant") {
    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = "M";
    article.append(avatar);
  }
  article.append(bubble);
  thread.append(article);
  article.scrollIntoView({ behavior: "smooth", block: "end" });
}

document.querySelector("#restore").addEventListener("click", async () => {
  state.textContent = "Reassembling identity...";
  try {
    const response = await fetch("/api/v1/import", {
      method: "POST",
      headers: sessionHeaders({ "content-type": "application/json" }),
      body: archive.value
    });
    const body = await response.json();
    if (!response.ok) throw new Error(body.error);
    personaId = body.id;
    personaName.textContent = body.name;
    connection.textContent = "Heat profile restored";
    sessionStatus.textContent = "ONLINE";
    sessionId.textContent = body.id.slice(0, 8).toUpperCase();
    state.textContent = "Meter reconnected. Thermal channel open.";
    message.disabled = false;
    chatButton.disabled = false;
    message.focus();
    addMessage("assistant", `${body.name} here. I translate notices, radiator noises, and the municipal meaning of 'soon'.`);
  } catch (error) {
    state.textContent = error.message;
    connection.textContent = "Heat profile interrupted";
  }
});


document.querySelector("#chat-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = message.value.trim();
  if (!personaId || !text) return;
  addMessage("user", text);
  message.value = "";
  message.disabled = true;
  chatButton.disabled = true;
  state.textContent = "Checking whether the boiler remembers...";
  try {
    const response = await fetch(`/api/personas/${personaId}/chat`, {
      method: "POST",
      headers: sessionHeaders({ "content-type": "application/json" }),
      body: JSON.stringify({ message: text })
    });
    const body = await response.json();
    if (!response.ok) throw new Error(body.error || "Conversation failed.");
    addMessage("assistant", body.reply);
    state.textContent = "Thermal channel holding.";
  } catch (error) {
    addMessage("assistant", `Connection anomaly: ${error.message}`);
    state.textContent = "The pipes need attention.";
  } finally {
    message.disabled = false;
    chatButton.disabled = false;
    message.focus();
  }
});
