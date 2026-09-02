const code = document.querySelector("#code");
const gutter = document.querySelector("#gutter");
const run = document.querySelector("#run");
const runLabel = document.querySelector("#run-label");
const consoleEl = document.querySelector("#console");
const status = document.querySelector("#status");
const statusText = document.querySelector("#status-text");

const snake = createSnake(document.querySelector("#snake"));

function createSnake(canvas) {
  const ctx = canvas.getContext("2d");
  const still = window.matchMedia("(prefers-reduced-motion: reduce)");
  const SEGMENTS = 52;
  const SPACING = 9;
  const SPEED = 245;
  const FADE_MS = 700;
  const MIN_VISIBLE_MS = 1600;

  const spine = [];
  let girth = 9;
  let heading = 0;
  let phase = 0;
  let target = { x: 0, y: 0 };
  let frame = 0;
  let stopTimer = 0;
  let last = 0;
  let shownAt = 0;

  function resize() {
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(window.innerWidth * ratio);
    canvas.height = Math.round(window.innerHeight * ratio);
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    girth = Math.max(6, Math.min(12, window.innerWidth * 0.011));
  }

  function aimSomewhereNew() {
    const margin = 80;
    target = {
      x: margin + Math.random() * Math.max(1, window.innerWidth - margin * 2),
      y: margin + Math.random() * Math.max(1, window.innerHeight - margin * 2)
    };
  }

  // Nose just past one edge with the body trailing off-screen, so the head shows almost at once.
  function spawn() {
    const edge = Math.floor(Math.random() * 4);
    const along = Math.random();
    const lead = 30;
    const spots = [
      { x: -lead, y: along * window.innerHeight, angle: 0 },
      { x: window.innerWidth + lead, y: along * window.innerHeight, angle: Math.PI },
      { x: along * window.innerWidth, y: -lead, angle: Math.PI / 2 },
      { x: along * window.innerWidth, y: window.innerHeight + lead, angle: -Math.PI / 2 }
    ];
    const spot = spots[edge];

    heading = spot.angle;
    phase = 0;
    spine.length = 0;
    for (let i = 0; i < SEGMENTS; i += 1) {
      spine.push({ x: spot.x - Math.cos(heading) * SPACING * i, y: spot.y - Math.sin(heading) * SPACING * i });
    }
    aimSomewhereNew();
  }

  function step(dt) {
    phase += dt * 6.4;

    const head = spine[0];
    const wanted = Math.atan2(target.y - head.y, target.x - head.x);
    const turn = 2.3 * dt;
    let delta = ((wanted - heading + Math.PI * 3) % (Math.PI * 2)) - Math.PI;
    heading += Math.max(-turn, Math.min(turn, delta));

    // The head weaves side to side; the rope-follow below turns that weave into body waves.
    const angle = heading + Math.sin(phase) * 0.62;
    head.x += Math.cos(angle) * SPEED * dt;
    head.y += Math.sin(angle) * SPEED * dt;
    if (Math.hypot(target.x - head.x, target.y - head.y) < 110) aimSomewhereNew();

    for (let i = 1; i < spine.length; i += 1) {
      const node = spine[i];
      const ahead = spine[i - 1];
      const dx = node.x - ahead.x;
      const dy = node.y - ahead.y;
      const pull = SPACING / (Math.hypot(dx, dy) || 1);
      node.x = ahead.x + dx * pull;
      node.y = ahead.y + dy * pull;
    }
  }

  function radiusAt(t) {
    return girth * (1 - 0.42 * t) * Math.min(1, (1 - t) * 4);
  }

  function traceBody() {
    const left = [];
    const right = [];

    for (let i = 0; i < spine.length; i += 1) {
      const prev = spine[Math.max(0, i - 1)];
      const next = spine[Math.min(spine.length - 1, i + 1)];
      const dx = next.x - prev.x;
      const dy = next.y - prev.y;
      const len = Math.hypot(dx, dy) || 1;
      const radius = radiusAt(i / (spine.length - 1));
      const nx = (-dy / len) * radius;
      const ny = (dx / len) * radius;
      left.push([spine[i].x + nx, spine[i].y + ny]);
      right.push([spine[i].x - nx, spine[i].y - ny]);
    }

    ctx.beginPath();
    ctx.moveTo(left[0][0], left[0][1]);
    for (let i = 1; i < left.length; i += 1) ctx.lineTo(left[i][0], left[i][1]);
    for (let i = right.length - 1; i >= 0; i -= 1) ctx.lineTo(right[i][0], right[i][1]);
    ctx.closePath();
  }

  function drawScales() {
    ctx.fillStyle = "rgba(20, 40, 16, .38)";
    for (let i = 3; i < spine.length - 8; i += 4) {
      const prev = spine[i - 1];
      const next = spine[i + 1];
      const size = radiusAt(i / (spine.length - 1)) * 0.5;
      ctx.save();
      ctx.translate(spine[i].x, spine[i].y);
      ctx.rotate(Math.atan2(next.y - prev.y, next.x - prev.x));
      ctx.beginPath();
      ctx.moveTo(size * 1.6, 0);
      ctx.lineTo(0, size);
      ctx.lineTo(-size * 1.6, 0);
      ctx.lineTo(0, -size);
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    }
  }

  function drawHead() {
    const head = spine[0];
    const angle = Math.atan2(head.y - spine[1].y, head.x - spine[1].x);

    ctx.save();
    ctx.translate(head.x, head.y);
    ctx.rotate(angle);

    const flick = phase % 7;
    if (flick < 1) {
      const reach = girth * (1.9 + Math.sin(flick * Math.PI) * 1.5);
      ctx.strokeStyle = "#ec8c7d";
      ctx.lineWidth = Math.max(1, girth * 0.16);
      ctx.beginPath();
      ctx.moveTo(girth * 1.2, 0);
      ctx.lineTo(reach, 0);
      ctx.moveTo(reach, 0);
      ctx.lineTo(reach + girth * 0.5, -girth * 0.35);
      ctx.moveTo(reach, 0);
      ctx.lineTo(reach + girth * 0.5, girth * 0.35);
      ctx.stroke();
    }

    ctx.fillStyle = "#b5da85";
    ctx.beginPath();
    ctx.ellipse(girth * 0.25, 0, girth * 1.55, girth * 1.05, 0, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "#1b2617";
    for (const side of [-1, 1]) {
      ctx.beginPath();
      ctx.ellipse(girth * 0.55, side * girth * 0.5, girth * 0.3, girth * 0.26, 0, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.fillStyle = "#e5b969";
    for (const side of [-1, 1]) {
      ctx.beginPath();
      ctx.arc(girth * 0.62, side * girth * 0.5, girth * 0.12, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.restore();
  }

  function draw() {
    ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);

    const head = spine[0];
    const tail = spine[spine.length - 1];
    const skin = ctx.createLinearGradient(head.x, head.y, tail.x, tail.y);
    skin.addColorStop(0, "#a7cf78");
    skin.addColorStop(0.55, "#7cae55");
    skin.addColorStop(1, "#4d7a3a");

    ctx.save();
    ctx.shadowColor = "rgba(0, 0, 0, .45)";
    ctx.shadowBlur = 22;
    ctx.shadowOffsetY = 12;
    traceBody();
    ctx.fillStyle = skin;
    ctx.fill();
    ctx.restore();

    traceBody();
    ctx.strokeStyle = "rgba(30, 52, 24, .55)";
    ctx.lineWidth = 1.2;
    ctx.stroke();

    drawScales();
    drawHead();
  }

  function tick(now) {
    const dt = Math.min((now - last) / 1000, 0.05);
    last = now;
    step(dt);
    draw();
    frame = requestAnimationFrame(tick);
  }

  return {
    start() {
      if (still.matches) return;
      clearTimeout(stopTimer);
      stopTimer = 0;
      shownAt = performance.now();
      canvas.classList.add("slithering");
      if (frame) return;
      resize();
      spawn();
      last = shownAt;
      frame = requestAnimationFrame(tick);
    },
    // Quick runs finish in milliseconds, so hold the snake on screen long enough to be seen.
    stop() {
      if (!frame || stopTimer) return;
      stopTimer = window.setTimeout(() => {
        canvas.classList.remove("slithering");
        stopTimer = window.setTimeout(() => {
          cancelAnimationFrame(frame);
          frame = 0;
          stopTimer = 0;
          ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
        }, FADE_MS);
      }, Math.max(0, MIN_VISIBLE_MS - (performance.now() - shownAt)));
    },
    resize() {
      if (frame) resize();
    }
  };
}

function syncEditor() {
  const lines = code.value.split("\n").length;
  gutter.textContent = Array.from({ length: lines }, (_, index) => index + 1).join("\n");
  gutter.scrollTop = code.scrollTop;
}

function setStatus(kind, label) {
  status.className = `status ${kind}`;
  statusText.textContent = label;
}

async function execute() {
  if (run.disabled || !code.value.trim()) return;

  run.disabled = true;
  runLabel.textContent = "Observing…";
  setStatus("running", "Running");
  snake.start();
  consoleEl.className = "console";
  consoleEl.textContent = "Starting fresh Python process…";

  try {
    const response = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: code.value })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || `Request failed (${response.status})`);

    consoleEl.replaceChildren();
    if (result.stdout) consoleEl.append(document.createTextNode(result.stdout));
    if (result.stderr) {
      const error = document.createElement("span");
      error.className = "stderr";
      error.textContent = result.stderr;
      consoleEl.append(error);
    }
    if (!result.stdout && !result.stderr) {
      consoleEl.className = "console empty";
      consoleEl.textContent = "Process completed without output.";
    }

    const failed = result.timed_out || result.signal !== null || result.exit_code !== 0;
    const resultLabel = result.timed_out ? "Timed out" : result.signal !== null ? "Killed" : failed ? "Error" : "Complete";
    setStatus(failed ? "error" : "success", resultLabel);
  } catch (error) {
    consoleEl.className = "console";
    consoleEl.textContent = error instanceof Error ? error.message : "Unknown request error";
    setStatus("error", "Request failed");
  } finally {
    run.disabled = false;
    runLabel.textContent = "Run specimen";
    snake.stop();
  }
}

code.addEventListener("input", syncEditor);
code.addEventListener("scroll", () => { gutter.scrollTop = code.scrollTop; });
code.addEventListener("keydown", event => {
  if (event.key === "Tab") {
    event.preventDefault();
    const start = code.selectionStart;
    code.setRangeText("    ", start, code.selectionEnd, "end");
    syncEditor();
  }
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
    event.preventDefault();
    execute();
  }
});
run.addEventListener("click", execute);
window.addEventListener("resize", () => snake.resize());
syncEditor();
