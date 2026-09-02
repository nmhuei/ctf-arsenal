"use client";

import { ChangeEvent, DragEvent, FormEvent, useEffect, useMemo, useState } from "react";

type Avatar = {
  id: number;
  name: string;
  date: string;
  tone: string;
  accent: string;
  image?: string;
};

type User = { id: number; username: string; email: string };
type ApiState = { ok: boolean; message?: string; csrf: string; user: User | null; avatars: Avatar[] };

const flashMessages: Record<string, string> = {
  "sign-in-required": "Please sign in to view that avatar.",
  "avatar-unavailable": "That avatar is unavailable or does not belong to your account.",
};

const placeholderAvatar: Avatar = {
  id: 0,
  name: "awaiting-signal.avif",
  date: "NOT YET FORGED",
  tone: "#ff5ab7",
  accent: "#6629ff",
};

function AvatarArt({ avatar, large = false }: { avatar: Avatar; large?: boolean }) {
  if (avatar.image) {
    return (
      <div className={`avatar-art ${large ? "avatar-art-large" : ""}`}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={avatar.image} alt="" />
      </div>
    );
  }

  return (
    <div
      className={`avatar-art generated-art ${large ? "avatar-art-large" : ""}`}
      style={{ "--tone": avatar.tone, "--accent": avatar.accent } as React.CSSProperties}
      aria-hidden="true"
    >
      <span className="art-orbit orbit-one" />
      <span className="art-orbit orbit-two" />
      <span className="art-head">
        <i className="art-eye eye-left" />
        <i className="art-eye eye-right" />
        <i className="art-mouth" />
      </span>
      <span className="art-star star-one">✦</span>
      <span className="art-star star-two">✦</span>
    </div>
  );
}

export default function Home() {
  const [avatars, setAvatars] = useState<Avatar[]>([]);
  const [selectedId, setSelectedId] = useState(0);
  const [user, setUser] = useState<User | null>(null);
  const [csrf, setCsrf] = useState("");
  const [loading, setLoading] = useState(true);
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [authBusy, setAuthBusy] = useState(false);
  const [query, setQuery] = useState("");
  const [watermark, setWatermark] = useState("MYAVATAR APP");
  const [opacity, setOpacity] = useState(68);
  const [dropActive, setDropActive] = useState(false);
  const [toast, setToast] = useState("");
  const [menuOpen, setMenuOpen] = useState(false);

  const selected = avatars.find((avatar) => avatar.id === selectedId) ?? avatars[0] ?? placeholderAvatar;
  const filtered = useMemo(
    () => avatars.filter((avatar) => avatar.name.toLowerCase().includes(query.toLowerCase())),
    [avatars, query],
  );

  async function loadState() {
    const response = await fetch("/api.php", { credentials: "same-origin", cache: "no-store" });
    const data = await response.json() as ApiState;
    setUser(data.user);
    setCsrf(data.csrf);
    setAvatars(data.avatars ?? []);
    setSelectedId((current) => current || data.avatars?.[0]?.id || 0);
    setLoading(false);
  }

  useEffect(() => {
    const url = new URL(window.location.href);
    const flashCode = url.searchParams.get("flash") ?? "";
    const flashMessage = flashMessages[flashCode];
    if (flashMessage) {
      showToast(flashMessage);
      url.searchParams.delete("flash");
      window.history.replaceState(null, "", `${url.pathname}${url.search}${url.hash}`);
    }

    const timer = window.setTimeout(() => {
      loadState().catch(() => {
        setLoading(false);
        showToast("Backend connection lost. Try refreshing.");
      });
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  function showToast(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(""), 2600);
  }

  async function addFile(file?: File) {
    if (!file) return;
    const extension = file.name.split(".").pop()?.toLowerCase();
    if (extension !== "avif" && file.type !== "image/avif") {
      showToast("AVIF files only — keep it crisp.");
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      showToast("That file is over the 5 MB limit.");
      return;
    }

    const body = new FormData();
    body.set("action", "upload");
    body.set("csrf_token", csrf);
    body.set("avatar", file);

    try {
      const response = await fetch("/api.php", { method: "POST", body, credentials: "same-origin" });
      const data = await response.json() as ApiState;
      setCsrf(data.csrf);
      if (!data.ok) {
        showToast(data.message ?? "The forge rejected that file.");
        return;
      }
      setAvatars(data.avatars);
      setSelectedId(data.avatars[0]?.id ?? 0);
      showToast(data.message ?? "Avatar forged and watermarked.");
    } catch {
      showToast("Upload failed. Check the backend connection.");
    }
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setDropActive(false);
    void addFile(event.dataTransfer.files[0]);
  }

  function handleFile(event: ChangeEvent<HTMLInputElement>) {
    void addFile(event.target.files?.[0]);
    event.target.value = "";
  }

  async function handleAuth(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setAuthBusy(true);
    const body = new FormData(event.currentTarget);
    body.set("action", authMode === "login" ? "login" : "signup");
    body.set("csrf_token", csrf);
    try {
      const response = await fetch("/api.php", { method: "POST", body, credentials: "same-origin" });
      const data = await response.json() as ApiState;
      setCsrf(data.csrf);
      if (!data.ok) {
        showToast(data.message ?? "Authentication failed.");
        return;
      }
      setUser(data.user);
      setAvatars(data.avatars);
      setSelectedId(data.avatars[0]?.id ?? 0);
      showToast(data.message ?? "Welcome to the forge.");
    } catch {
      showToast("Backend connection lost. Try again.");
    } finally {
      setAuthBusy(false);
    }
  }

  async function logout() {
    const body = new FormData();
    body.set("action", "logout");
    body.set("csrf_token", csrf);
    try {
      const response = await fetch("/api.php", { method: "POST", body, credentials: "same-origin" });
      const data = await response.json() as ApiState;
      setMenuOpen(false);
      setUser(null);
      setAvatars([]);
      setSelectedId(0);
      setCsrf(data.csrf);
      showToast(data.message ?? "Signed out.");
      await loadState();
    } catch {
      showToast("Could not sign out.");
    }
  }

  if (loading) {
    return (
      <main className="auth-stage loading-stage">
        <div className="ambient-grid" aria-hidden="true" />
        <div className="brand-cube auth-cube" aria-hidden="true"><i /></div>
        <p>CALIBRATING IDENTITY FORGE…</p>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="auth-stage">
        <div className="ambient-grid" aria-hidden="true" />
        <div className="auth-orbit auth-orbit-a" aria-hidden="true" />
        <div className="auth-orbit auth-orbit-b" aria-hidden="true" />
        <section className="auth-poster">
          <div className="brand" aria-label="MyAvatar">
            <span className="brand-cube" aria-hidden="true"><i /></span>
            <span>MYAVATAR<small>IDENTITY FORGE</small></span>
          </div>
          <p className="eyebrow"><span>✦</span> AUTHENTICATION PORTAL / SECURE</p>
          <h1>ENTER THE<br /><em>FORGE.</em></h1>
          <p>One account. Infinite identities. Every upload stamped, secured, and stored in your private vault.</p>
          <div className="auth-stamp">AVIF<br /><b>ONLY</b></div>
        </section>

        <section className="auth-console">
          <div className="auth-tabs">
            <button className={authMode === "login" ? "active" : ""} onClick={() => setAuthMode("login")}>SIGN IN</button>
            <button className={authMode === "register" ? "active" : ""} onClick={() => setAuthMode("register")}>CREATE ID</button>
          </div>
          <div className="panel-index">{authMode === "login" ? "01" : "02"}</div>
          <p className="console-label">IDENTITY CHECK</p>
          <h2>{authMode === "login" ? <>WELCOME<br />BACK.</> : <>NEW<br />SIGNAL.</>}</h2>
          <form className="auth-form" onSubmit={handleAuth}>
            {authMode === "register" && (
              <>
                <label>USERNAME<input name="username" autoComplete="username" required minLength={3} maxLength={30} /></label>
                <label>EMAIL<input name="email" type="email" autoComplete="email" required /></label>
              </>
            )}
            {authMode === "login" && (
              <label>USERNAME OR EMAIL<input name="identity" autoComplete="username" required /></label>
            )}
            <label>PASSWORD<input name="password" type="password" autoComplete={authMode === "login" ? "current-password" : "new-password"} minLength={8} required /></label>
            {authMode === "register" && (
              <label>CONFIRM PASSWORD<input name="confirm_password" type="password" autoComplete="new-password" minLength={8} required /></label>
            )}
            <button className="forge-button" type="submit" disabled={authBusy}>
              <span>{authBusy ? "VERIFYING…" : authMode === "login" ? "ENTER STUDIO" : "FORGE ACCOUNT"}</span><b>↗</b>
            </button>
          </form>
          <p className="auth-switch">
            {authMode === "login" ? "NEW TO THE LAB?" : "ALREADY REGISTERED?"}
            <button onClick={() => setAuthMode(authMode === "login" ? "register" : "login")}>
              {authMode === "login" ? " CREATE YOUR ID" : " SIGN IN"}
            </button>
          </p>
        </section>
        {toast && <div className="toast" role="status"><span>✦</span>{toast}</div>}
      </main>
    );
  }

  return (
    <main className="site-shell">
      <div className="ambient-grid" aria-hidden="true" />
      <div className="ambient-blob blob-a" aria-hidden="true" />
      <div className="ambient-blob blob-b" aria-hidden="true" />

      <header className="topbar">
        <a className="brand" href="#studio" aria-label="MyAvatar home">
          <span className="brand-cube" aria-hidden="true">
            <i />
          </span>
          <span>
            MYAVATAR
            <small>IDENTITY FORGE</small>
          </span>
        </a>

        <nav className="nav-pills" aria-label="Primary navigation">
          <a className="active" href="#studio"><span>01</span> Studio</a>
          <a href="#vault"><span>02</span> Vault</a>
          <a href="#about"><span>03</span> About</a>
        </nav>

        <div className="account-wrap">
          <button className="account-button" onClick={() => setMenuOpen((open) => !open)} aria-expanded={menuOpen}>
            <span className="mini-face" aria-hidden="true">◉</span>
            <span><b>{user.username}</b><small>CREATOR_{String(user.id).padStart(3, "0")}</small></span>
            <span className="chevron">⌄</span>
          </button>
          {menuOpen && (
            <div className="account-menu">
              <p className="account-identity"><span>ACTIVE IDENTITY</span><b>{user.username}</b><small>{user.email}</small></p>
              <button type="button" className="logout" onClick={() => void logout()}>LOG OUT</button>
            </div>
          )}
        </div>
      </header>

      <section className="hero" id="studio">
        <div className="hero-copy">
          <p className="eyebrow"><span>✦</span> AVATAR LAB / SESSION 07</p>
          <h1>FORGE YOUR<br /><em>DIGITAL SELF.</em></h1>
          <p className="hero-intro">Upload once. Stamp your signature. Own every pixel of your online identity.</p>
          <div className="hero-stats">
            <div><b>{String(avatars.length).padStart(2, "0")}</b><span>IDENTITIES<br />FORGED</span></div>
            <div><b>5<small>MB</small></b><span>MAXIMUM<br />FIREPOWER</span></div>
            <div><b>∞</b><span>PURE<br />PERSONALITY</span></div>
          </div>
        </div>

        <div className="hero-object" aria-hidden="true">
          <div className="orbit-copy orbit-copy-top">YOUR FACE • YOUR MARK • YOUR RULES •</div>
          <div className="hero-ring ring-back" />
          <div className="hero-ring ring-front" />
          <div className="floating-card">
            <AvatarArt avatar={selected} large />
            <span className="card-watermark">{watermark || "MYAVATAR"}</span>
            <span className="scan-line" />
          </div>
          <span className="floating-chip chip-one">AVIF</span>
          <span className="floating-chip chip-two">512²</span>
          <span className="floating-spark spark-one">✦</span>
          <span className="floating-spark spark-two">✦</span>
        </div>
      </section>

      <section className="forge-grid" aria-label="Avatar forge">
        <div
          className={`upload-panel dimensional-panel ${dropActive ? "drop-active" : ""}`}
          onDragOver={(event) => { event.preventDefault(); setDropActive(true); }}
          onDragLeave={() => setDropActive(false)}
          onDrop={handleDrop}
        >
          <div className="panel-index">01</div>
          <div className="panel-heading">
            <p>INPUT MODULE</p>
            <h2>FEED THE<br />MACHINE.</h2>
          </div>
          <label className="drop-zone">
            <input type="file" accept=".avif,image/avif" onChange={handleFile} />
            <span className="drop-cube"><i /><b>＋</b></span>
            <strong>{dropActive ? "DROP IT LIKE IT’S HOT" : "DROP YOUR AVIF HERE"}</strong>
            <small>OR PUNCH THE BUTTON BELOW</small>
            <span className="upload-button">CHOOSE FILE <b>↗</b></span>
          </label>
          <div className="spec-strip">
            <span><i>FORMAT</i><b>AVIF ONLY</b></span>
            <span><i>LIMIT</i><b>5 MB</b></span>
            <span><i>DIMENSIONS</i><b>64—512 PX</b></span>
          </div>
        </div>

        <div className="editor-panel dimensional-panel">
          <div className="panel-index coral">02</div>
          <div className="panel-heading">
            <p>SIGNATURE MODULE</p>
            <h2>MAKE YOUR<br />MARK.</h2>
          </div>
          <div className="editor-body">
            <div className="preview-well">
              <AvatarArt avatar={selected} />
              <div className="watermark-preview" style={{ opacity: opacity / 100 }}>{watermark || "MYAVATAR"}</div>
              <span className="corner corner-tl" /><span className="corner corner-tr" />
              <span className="corner corner-bl" /><span className="corner corner-br" />
            </div>
            <div className="controls">
              <label>
                WATERMARK PREVIEW
                <input maxLength={24} value={watermark} onChange={(event) => setWatermark(event.target.value.toUpperCase())} />
                <span>{watermark.length}/24</span>
              </label>
              <label className="range-label">
                <span>PREVIEW OPACITY <b>{opacity}%</b></span>
                <input type="range" min="15" max="100" value={opacity} onChange={(event) => setOpacity(Number(event.target.value))} />
              </label>
              <button className="forge-button" onClick={() => showToast("Upload an AVIF in module 01 to forge it.")}>
                <span>READY TO FORGE</span><b>↗</b>
              </button>
            </div>
          </div>
        </div>
      </section>

      <section className="vault-section" id="vault">
        <div className="vault-heading">
          <div>
            <p className="eyebrow"><span>✦</span> PERSONAL ARCHIVE</p>
            <h2>YOUR AVATAR<br /><em>VAULT.</em></h2>
          </div>
          <div className="vault-tools">
            <label className="search-box">⌕<input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="SEARCH THE VAULT" /></label>
            <button onClick={() => setQuery("")}>ALL / {avatars.length}</button>
          </div>
        </div>

        <div className="avatar-grid">
          {filtered.map((avatar, index) => (
            <article
              className={`avatar-card ${avatar.id === selectedId ? "selected" : ""}`}
              key={avatar.id}
              onClick={() => setSelectedId(avatar.id)}
            >
              <div className="card-number">{String(index + 1).padStart(2, "0")}</div>
              <AvatarArt avatar={avatar} />
              <div className="avatar-card-info">
                <div><h3>{avatar.name}</h3><p>{avatar.date}</p></div>
                <a href={avatar.image} download={avatar.name} onClick={(event) => event.stopPropagation()} aria-label={`Download ${avatar.name}`}>↓</a>
              </div>
              <span className="card-status">● WATERMARKED</span>
            </article>
          ))}
        </div>
        {!filtered.length && <p className="empty-state">{avatars.length ? "NO SIGNAL. TRY ANOTHER SEARCH." : "VAULT EMPTY. FORGE YOUR FIRST AVATAR ABOVE."}</p>}
      </section>

      <section className="manifesto" id="about">
        <p>NO BORING<br />PROFILE PICS.</p>
        <div className="manifesto-mark">✦</div>
        <p>JUST YOU,<br />AMPLIFIED.</p>
      </section>

      <footer>
        <span>MYAVATAR © 2026</span>
        <span>BUILT FOR LOUD IDENTITIES</span>
        <a href="#studio">BACK TO THE FORGE ↑</a>
      </footer>

      {toast && <div className="toast" role="status"><span>✦</span>{toast}</div>}
    </main>
  );
}
