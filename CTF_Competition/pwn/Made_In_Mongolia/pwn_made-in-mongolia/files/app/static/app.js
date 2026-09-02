const code = document.querySelector("#code");
const runButton = document.querySelector("#run-button");
const resetButton = document.querySelector("#reset-button");
const output = document.querySelector("#output");
const empty = document.querySelector("#terminal-empty");
const status = document.querySelector("#run-status");
const runtime = document.querySelector("#runtime");
const lineNumbers = document.querySelector("#line-numbers");
const initialCode = code.value;

function updateLines() {
  const count = code.value.split("\n").length;
  lineNumbers.textContent = Array.from({ length: count }, (_, index) => index + 1).join("\n");
  lineNumbers.scrollTop = code.scrollTop;
}

function setStatus(kind, label) {
  status.className = `run-status ${kind}`;
  status.querySelector("span").textContent = label;
}

function appendText(value, className) {
  if (!value) return;
  const span = document.createElement("span");
  if (className) span.className = className;
  span.textContent = value;
  output.append(span);
}

async function run() {
  if (runButton.disabled) return;
  runButton.disabled = true;
  runButton.querySelector("span").textContent = "Running";
  empty.hidden = true;
  output.replaceChildren();
  runtime.textContent = "executing without a sandbox…";
  setStatus("running", "RUNNING");

  try {
    const response = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: code.value }),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Execution request failed.");

    appendText(result.stdout);
    appendText(result.stderr, "stderr");

    if (!result.stdout && !result.stderr) {
      appendText("(program produced no output)\n");
    }
    const succeeded = result.exit_code === 0;
    setStatus(succeeded ? "success" : "error", succeeded ? "FINISHED" : "FAILED");
    runtime.textContent = `${result.duration_ms} ms · exit ${result.exit_code ?? "unknown"}`;
  } catch (error) {
    appendText(`[playground] ${error.message}`, "stderr");
    setStatus("error", "ERROR");
    runtime.textContent = "request failed";
  } finally {
    runButton.disabled = false;
    runButton.querySelector("span").textContent = "Run code";
  }
}

code.addEventListener("input", updateLines);
code.addEventListener("scroll", () => { lineNumbers.scrollTop = code.scrollTop; });
code.addEventListener("keydown", (event) => {
  if (event.key === "Tab") {
    event.preventDefault();
    const start = code.selectionStart;
    code.setRangeText("    ", start, code.selectionEnd, "end");
    updateLines();
  }
  if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
    event.preventDefault();
    run();
  }
});

runButton.addEventListener("click", run);
resetButton.addEventListener("click", () => {
  code.value = initialCode;
  updateLines();
  code.focus();
});

updateLines();
